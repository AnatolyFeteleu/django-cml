from __future__ import absolute_import

import importlib
import logging
import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import List
from xml.etree.ElementTree import Element

import six

from .conf import settings
from .items import *
from .utils.translations import *

try:
    from xml.etree import cElementTree as ET  # NOQA
except ImportError:
    from xml.etree import ElementTree as ET  # NOQA


logger = logging.getLogger(__name__)


class ManagerMixin(object):

    @staticmethod
    def find(path, *, tree) -> 'Element':
        return (
            tree
            .find('{%s}%s' % (settings.CML_DOC_XMLNS, path))
        )

    @staticmethod
    def find_all(path, *, tree) -> List['Element']:
        return (
            tree.findall(
                '/'.join(map(
                    lambda d: '{%s}%s' % (settings.CML_DOC_XMLNS, d),
                    path.split('/')
                ))
            )
        )


class ImportManager(ManagerMixin):

    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = None
        self.item_processor = ItemProcessor()

    def import_all(self):
        try:
            self.tree = self._get_tree()
        except Exception as e:  # NOQA
            logger.error('Import all error!')
            return
        self.import_classifier()
        self.import_catalogue()
        self.import_offers_pack()
        self.import_orders()
        logger.info('Import success!')

    def _get_tree(self):
        if self.tree is not None:
            return self.tree
        if not os.path.exists(self.file_path):
            message = f'File not found {self.file_path}'
            logger.error(message)
            raise OSError(message)
        try:
            tree = ET.parse(self.file_path)
        except Exception as e:
            message = f'File parse error {self.file_path}'
            logger.error(message)
            raise e
        return tree

    @staticmethod
    def _get_cleaned_text(element):
        try:
            text = element.text
        except Exception as e:  # NOQA
            text = str()
        if text is None:
            return str()
        return text.strip(str())

    def import_classifier(self):
        try:
            tree = self._get_tree()
        except Exception as e:  # NOQA
            logger.error('Import classifier error!')
            return
        classifier_element = self.find(CLASSIFIER, tree=tree)
        if classifier_element is not None:
            self._parse_groups(classifier_element)
            self._parse_properties(classifier_element)
            self._parse_units_of_measurements(classifier_element)

    def _parse_groups(self, current_element, parent_item=None):
        for group_element in self.find_all(f'{GROUPS}/{GROUP}', tree=current_element):
            group_item = Group(group_element)
            group_item.id = self._get_cleaned_text(self.find(ID, tree=group_element))
            group_item.name = self._get_cleaned_text(self.find(TITLE, tree=group_element))
            if parent_item is not None:
                parent_item.groups.append(group_item)
            self._parse_groups(group_element, group_item)
            # processing only top level groups
            if parent_item is None:
                self.item_processor.process_item(group_item)

    def _parse_properties(self, current_element):
        for property_element in self.find_all(
                f'{PROPERTIES}/{PROPERTY}', tree=current_element):
            property_item = Property(property_element)
            property_item.id = self._get_cleaned_text(
                self.find(ID, tree=property_element))
            property_item.name = self._get_cleaned_text(
                self.find(TITLE, tree=property_element))
            property_item.value_type = self._get_cleaned_text(
                self.find(VALUE_TYPE, tree=property_element))
            property_item.for_products = self._get_cleaned_text(
                self.find(FOR_GOODS, tree=property_element)) == TRUE
            self.item_processor.process_item(property_item)

            for variant_element in self.find_all(
                    f'{VARIATIONS_REFERENCES}/{property_item.value_type}',
                    tree=property_element):
                variant = PropertyVariant(variant_element)
                variant.id = self._get_cleaned_text(self.find(VALUE_ID, tree=variant_element))
                variant.value = self._get_cleaned_text(self.find(VALUE, tree=variant_element))
                variant.property_id = property_item.id
                self.item_processor.process_item(variant)

    def _parse_units_of_measurements(self, current_element):
        for unit_element in self.find_all(f'{UNITS_OF_MEASUREMENT}/{UNIT_OF_MEASUREMENT}', tree=current_element):
            unit_item = UnitOfMeasurementItem(unit_element)
            unit_item.code = self._get_cleaned_text(
                self.find(CODE, tree=unit_element))
            unit_item.title_full = self._get_cleaned_text(
                self.find(TITLE_FULL, tree=unit_element))
            unit_item.intern_title_short = self._get_cleaned_text(
                self.find(INTERNATIONAL_TITLE_SHORT, tree=unit_element))

    def import_catalogue(self):
        try:
            tree = self._get_tree()
        except Exception as e:  # NOQA
            logger.error('Import catalogue error!')
            return

        catalogue_element = self.find(CATALOG, tree=tree)
        if catalogue_element is not None:
            self._parse_products(catalogue_element)

    def _parse_products(self, current_element):
        for product_element in self.find_all(
                f'{ITEMS}/{ITEM}', tree=current_element):
            product_item = Product(product_element)
            product_item.id = self._get_cleaned_text(
                self.find(ID, tree=product_element))
            product_item.name = self._get_cleaned_text(
                self.find(TITLE, tree=product_element))
            product_item.item_number = self._get_cleaned_text(
                self.find(ITEM_NUMBER, tree=product_element))

            sku_element = self.find(BASIC_UNIT, tree=product_element)

            if sku_element is not None:
                sku_item = Sku(sku_element)
                sku_item.id = sku_element.get(CODE)
                sku_item.name_full = sku_element.get(TITLE_FULL)
                sku_item.international_abbr = sku_element.get(INTERNATIONAL_ABBR)
                sku_item.name = self._get_cleaned_text(sku_element)
                product_item.sku_id = sku_item.id
                self.item_processor.process_item(sku_item)

            image_element = self.find(IMAGE, tree=product_element)
            if image_element is not None:
                image_text = self._get_cleaned_text(image_element)

                try:
                    image_filename = os.path.basename(image_text)
                except Exception as e:  # NOQA
                    image_filename = str()

                if image_filename:
                    product_item.image_path = os.path.join(
                        settings.CML_UPLOAD_ROOT, image_filename)

            for group_id_element in self.find_all(
                    f'{GROUPS}/{ID}', tree=product_element):
                product_item.group_ids.append(
                    self._get_cleaned_text(group_id_element))

            for property_element in self.find_all(
                    f'{PROPERTIES_VALUES}/{PROPERTY_VALUES}',
                    tree=product_element):
                property_id = self._get_cleaned_text(
                    self.find(ID, tree=property_element))
                property_variant_id = self._get_cleaned_text(
                    self.find(VALUE, tree=property_element))

                if property_variant_id:
                    product_item.properties.append((property_id, property_variant_id))

            for tax_element in self.find_all(
                    f'{TAX_RATES}/{TAX_RATE}', tree=product_element):
                tax_item = Tax(tax_element)
                tax_item.name = self._get_cleaned_text(
                    self.find(TITLE, tree=tax_element))

                try:
                    tax_item.value = Decimal(self._get_cleaned_text(
                        self.find(BET, tree=tax_element)))
                except Exception as e:  # NOQA
                    tax_item.value = Decimal()

                self.item_processor.process_item(tax_item)
                product_item.tax_name = tax_item.name

            for additional_field_element in self.find_all(
                    f'{THE_VALUES_OF_THE_DETAILS}/{THE_VALUE_OF_THE_PROPS}',
                    tree=product_element):
                additional_field = AdditionalField(additional_field_element)
                additional_field.name = self._get_cleaned_text(
                    self.find(TITLE, tree=additional_field_element))
                additional_field.value = self._get_cleaned_text(
                    self.find(VALUE, tree=additional_field_element))
                product_item.additional_fields.append(additional_field)
            self.item_processor.process_item(product_item)

    def import_offers_pack(self):
        try:
            tree = self._get_tree()
        except Exception as e:  # NOQA
            logger.error('Import offers pack error!')
            return
        offers_pack_element = self.find(PACKAGE_OF_OFFERS, tree=tree)
        if offers_pack_element is not None:
            self._parse_price_types(offers_pack_element)
            self._parse_offers(offers_pack_element)

    def _parse_price_types(self, current_element):
        for price_type_element in self.find_all(
                f'{TYPES_OF_PRICES}/{PRICE_TYPE}',
                tree=current_element):
            price_type_item = PriceType(price_type_element)
            price_type_item.id = self._get_cleaned_text(
                self.find(ID, tree=price_type_element))
            price_type_item.name = self._get_cleaned_text(
                self.find(TITLE, tree=price_type_element))
            price_type_item.currency = self._get_cleaned_text(
                self.find(CURRENCY, tree=price_type_element))
            price_type_item.tax_name = self._get_cleaned_text(
                self.find(f'{TAX}/{TITLE}', tree=price_type_element))
            if self._get_cleaned_text(self.find(
                    f'{TAX}/{TAKEN_INTO_ACCOUNT_IN_THE_AMOUNT}',
                    tree=price_type_element)) == TRUE:
                price_type_item.tax_in_sum = True
            self.item_processor.process_item(price_type_item)

    def _parse_offers(self, current_element):
        for offer_element in self.find_all(
                f'{OFFERS}/{OFFER}', tree=current_element):
            offer_item = Offer(offer_element)
            offer_item.id = self._get_cleaned_text(self.find(ID, tree=offer_element))
            offer_item.name = self._get_cleaned_text(self.find(TITLE, tree=offer_element))

            sku_element = self.find(BASIC_UNIT, tree=offer_element)
            if sku_element is not None:
                sku_item = Sku(sku_element)
                sku_item.id = sku_element.get(CODE)
                sku_item.name_full = sku_element.get(TITLE_FULL)
                sku_item.international_abbr = sku_element.get(INTERNATIONAL_ABBR)
                sku_item.name = self._get_cleaned_text(sku_element)
                offer_item.sku_id = sku_item.id
                self.item_processor.process_item(sku_item)

            for price_element in self.find_all(
                    f'{PRICES}/{PRICE}', tree=offer_element):
                price_item = Price(price_element)
                price_item.representation = self._get_cleaned_text(
                    self.find(PERFORMANCE, tree=price_element))
                price_item.price_type_id = self._get_cleaned_text(
                    self.find(PRICE_TYPE_ID, tree=price_element))
                price_item.price_for_sku = Decimal(self._get_cleaned_text(
                    self.find(PRICE_PER_UNIT, tree=price_element)))
                price_item.currency_name = self._get_cleaned_text(
                    self.find(CURRENCY, tree=price_element))
                price_item.sku_name = self._get_cleaned_text(
                    self.find(UNIT, tree=price_element))
                price_item.sku_ratio = Decimal(self._get_cleaned_text(
                    self.find(RATIO, tree=price_element)))
                offer_item.prices.append(price_item)

            self.item_processor.process_item(offer_item)

    def import_orders(self):
        try:
            tree = self._get_tree()
        except Exception as e:  # NOQA
            logger.error('Import orders error!')
            return
        orders_elements = self.find(DOCUMENT, tree=tree)
        if orders_elements is not None:
            self._parse_orders(orders_elements)

    def _parse_orders(self, order_elements):
        for order_element in order_elements:
            order_item = Order(order_element)
            order_item.id = self._get_cleaned_text(
                self.find(ID, tree=order_element))
            order_item.number = self._get_cleaned_text(
                self.find(NUMBER, tree=order_element))
            order_item.date = self._get_cleaned_text(
                self.find(DATE, tree=order_element))
            order_item.currency_name = self._get_cleaned_text(
                self.find(CURRENCY, tree=order_element))
            order_item.currency_rate = self._get_cleaned_text(
                self.find(CURRENCY, tree=order_element))
            order_item.operation = self._get_cleaned_text(
                self.find(HOUSEHOLD_OPERATION, tree=order_element))
            order_item.role = self._get_cleaned_text(
                self.find(ROLE, tree=order_element))
            order_item.sum = self._get_cleaned_text(
                self.find(AMOUNT, tree=order_element))
            order_item.client.id = self._get_cleaned_text(
                self.find(f'{COUNTERPARTIES}/{COUNTERPARTY}/{ID}',
                          tree=order_element))
            order_item.client.name = self._get_cleaned_text(
                self.find(f'{COUNTERPARTIES}/{COUNTERPARTY}/{TITLE}',
                          tree=order_element))
            order_item.client.full_name = self._get_cleaned_text(
                self.find(f'{COUNTERPARTIES}/{COUNTERPARTY}/{FULL_NAME}',
                          tree=order_element))
            order_item.time = self._get_cleaned_text(
                self.find(TIME, tree=order_element))
            order_item.comment = self._get_cleaned_text(
                self.find(COMMENT, tree=order_element))
            item_elements = self.find(
                f'{PRODUCTS}/{PRODUCT}', tree=order_element)

            if item_elements is not None:
                for item_element in item_elements:
                    order_item_item = OrderItem(item_element)  # NOQA
                    order_item_item.id = self._get_cleaned_text(
                        self.find(ID, tree=item_element))
                    order_item_item.name = self._get_cleaned_text(
                        self.find(TITLE, tree=item_element))
                    sku_element = self.find(BASIC_UNIT, tree=item_element)

                    if sku_element is not None:
                        order_item_item.sku.id = sku_element.get(CODE)
                        order_item_item.sku.name = self._get_cleaned_text(
                            sku_element)
                        order_item_item.sku.name_full = sku_element.get(
                            TITLE_FULL)
                        order_item_item.sku.international_abbr = sku_element.get(
                            INTERNATIONAL_ABBR)

                    order_item_item.price = self._get_cleaned_text(
                        self.find(PRICE_PER_UNIT, tree=item_element))
                    order_item_item.quant = self._get_cleaned_text(
                        self.find(QUANTITY, tree=item_element))
                    order_item_item.sum = self._get_cleaned_text(
                        self.find(AMOUNT, tree=item_element))
                    order_item.items.append(order_item_item)

                    additional_field_elements = self.find(
                        f'{THE_VALUES_OF_THE_DETAILS}/{THE_VALUE_OF_THE_PROPS}',
                        tree=order_element
                    )
                    if additional_field_elements is not None:
                        for additional_field_element in additional_field_elements:
                            additional_field_item = AdditionalField(additional_field_element)
                            additional_field_item.name = self._get_cleaned_text(
                                self.find(TITLE, tree=item_element))
                            additional_field_item.value = self._get_cleaned_text(
                                self.find(VALUE, tree=item_element))
            self.item_processor.process_item(order_item)


class ExportManager(object):

    def __init__(self):
        self.item_processor = ItemProcessor()
        self.root = ET.Element(COMMERCIAL_INFORMATION)
        self.root.set(VERSIONS_OF_THE_SCHEME, '2.05')
        self.root.set(DATA_FORMATIONS, six.text_type(datetime.now().date()))

    def get_xml(self):
        f = BytesIO()
        tree = ET.ElementTree(self.root)
        tree.write(f, encoding='windows-1251', xml_declaration=True)
        return f.getvalue()

    def export_all(self):
        self.export_orders()

    def export_orders(self):
        for order in self.item_processor.yield_item(Order):
            order_element = ET.SubElement(self.root, DOCUMENT)
            ET.SubElement(order_element, ID).text = six.text_type(order.id)
            ET.SubElement(order_element, NUMBER).text = six.text_type(
                order.number)
            ET.SubElement(order_element, DATE).text = six.text_type(
                order.date.strftime('%Y-%m-%d'))
            ET.SubElement(order_element, TIME).text = six.text_type(
                order.time.strftime('%H:%M:%S'))
            ET.SubElement(order_element, HOUSEHOLD_OPERATION).text = six.text_type(
                order.operation)
            ET.SubElement(order_element, ROLE).text = six.text_type(order.role)
            ET.SubElement(order_element, CURRENCY).text = six.text_type(
                order.currency_name)
            ET.SubElement(order_element, EXCHANGE_RATE).text = six.text_type(
                order.currency_rate)
            ET.SubElement(order_element, AMOUNT).text = six.text_type(order.sum)
            ET.SubElement(order_element, COMMENT).text = six.text_type(
                order.comment)
            clients_element = ET.SubElement(order_element, COUNTERPARTIES)
            client_element = ET.SubElement(clients_element, COUNTERPARTY)
            ET.SubElement(client_element, ID).text = six.text_type(
                order.client.id)
            ET.SubElement(client_element, NAME).text = six.text_type(
                order.client.name)
            ET.SubElement(client_element, ROLE).text = six.text_type(
                order.client.role)
            ET.SubElement(client_element, FULL_NAME).text = six.text_type(
                order.client.full_name)
            ET.SubElement(client_element, SURNAME).text = six.text_type(
                order.client.last_name)
            ET.SubElement(client_element, NAME).text = six.text_type(
                order.client.first_name)

            # address_element = ET.SubElement(clients_element, REGISTRATION_ADDRESS)

            ET.SubElement(clients_element, PERFORMANCE).text = six.text_type(
                order.client.address)
            products_element = ET.SubElement(order_element, ITEMS)

            for order_item in order.items:
                product_element = ET.SubElement(products_element, ITEM)
                ET.SubElement(product_element, ID).text = six.text_type(
                    order_item.id)
                ET.SubElement(product_element, TITLE).text = six.text_type(
                    order_item.name)
                sku_element = ET.SubElement(product_element, BASIC_UNIT)
                sku_element.set(CODE, order_item.sku.id)
                sku_element.set(TITLE_FULL, order_item.sku.name_full)
                sku_element.set(
                    INTERNATIONAL_ABBR, order_item.sku.international_abbr)
                sku_element.text = order_item.sku.name

                ET.SubElement(product_element, PRICE_PER_UNIT).text = six.text_type(
                    order_item.price)
                ET.SubElement(product_element, QUANTITY).text = six.text_type(
                    order_item.quant)
                ET.SubElement(product_element, AMOUNT).text = six.text_type(
                    order_item.sum)

    def flush(self):
        self.item_processor.flush_pipeline(Order)


class ItemProcessor(ManagerMixin):

    def __init__(self):
        self._project_pipelines = {}
        self._load_project_pipelines()

    def _load_project_pipelines(self):
        try:
            pipelines_module_name = settings.CML_PROJECT_PIPELINES
        except AttributeError:
            logger.info('Configure CML_PROJECT_PIPELINES in settings!')
            return
        try:
            pipelines_module = importlib.import_module(pipelines_module_name)
        except ImportError:
            return
        for item_class_name in PROCESSED_ITEMS:
            try:
                pipeline_class = getattr(pipelines_module, f'{item_class_name}Pipeline')
            except AttributeError:
                continue
            self._project_pipelines[item_class_name] = pipeline_class()

    def _get_project_pipeline(self, item_class):
        item_class_name = item_class.__name__
        return self._project_pipelines.get(item_class_name, False)

    def process_item(self, item):
        project_pipeline = self._get_project_pipeline(item.__class__)
        if project_pipeline:
            try:
                project_pipeline.process_item(item)  # NOQA
            except Exception as e:
                logger.error(
                    f'Error processing of item {item.__class__.__name__}: '
                    f'{repr(e)}'
                )

    def yield_item(self, item_class):
        project_pipeline = self._get_project_pipeline(item_class)
        if project_pipeline:
            try:
                return project_pipeline.yield_item()  # NOQA
            except Exception as e:
                logger.error(f'Error yielding item {item_class.__name__}: '
                             f'{repr(e)}')
                return []
        return []

    def flush_pipeline(self, item_class):
        project_pipeline = self._get_project_pipeline(item_class)
        if project_pipeline:
            try:
                project_pipeline.flush()  # NOQA
            except Exception as e:
                logger.error(f'Error flushing pipeline for item {item_class.__name__}: '
                             f'{repr(e)}')
