from __future__ import absolute_import

from datetime import datetime
from decimal import Decimal

from .utils.translations import *

PROCESSED_ITEMS = (
    'Group', 'PropertyVariant', 'Property', 'PropertyVariant', 'Sku', 'Tax',
    'Product', 'Offer', 'Order', 'UnitOfMeasurementItem'
)

__all__ = (
    'BaseItem',
    'Group',
    'Property',
    'PropertyVariant',
    'Sku',
    'Tax',
    'AdditionalField',
    'Product',
    'PriceType',
    'Price',
    'Offer',
    'Client',
    'OrderItem',
    'Order',
    'UnitOfMeasurementItem',
    'PROCESSED_ITEMS',
)


class BaseItem(object):

    def __init__(self, xml_element=None):
        self.xml_element = xml_element


class UnitOfMeasurementItem(BaseItem):

    def __init__(self, *args, **kwargs):
        super(UnitOfMeasurementItem, self).__init__(*args, **kwargs)

        self.code = str()
        self.title_full = str()
        self.intern_title_short = str()


class Group(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)

        self.id = str()
        self.name = str()
        self.groups = list()


class Property(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Property, self).__init__(*args, **kwargs)

        self.id = str()
        self.name = str()
        self.value_type = str()
        self.for_products = False


class PropertyVariant(BaseItem):

    def __init__(self, *args, **kwargs):
        super(PropertyVariant, self).__init__(*args, **kwargs)

        self.id = str()
        self.value = str()
        self.property_id = str()


class Sku(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Sku, self).__init__(*args, **kwargs)

        self.id = str()
        self.name = str()
        self.name_full = str()
        self.international_abbr = str()


class Tax(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Tax, self).__init__(*args, **kwargs)

        self.name = str()
        self.value = Decimal()


class AdditionalField(BaseItem):

    def __init__(self, *args, **kwargs):
        super(AdditionalField, self).__init__(*args, **kwargs)

        self.name = str()
        self.value = str()


class Product(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)

        self.id = str()
        self.name = str()
        self.item_number = str()
        self.sku_id = str()
        self.group_ids = list()
        self.properties = list()
        self.tax_name = str()
        self.image_path = str()
        self.image_filename = str()
        self.additional_fields = list()


class PriceType(BaseItem):

    def __init__(self, *args, **kwargs):
        super(PriceType, self).__init__(*args, **kwargs)

        self.id = str()
        self.name = str()
        self.currency = str()
        self.tax_name = str()
        self.tax_in_sum = False


class Price(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Price, self).__init__(*args, **kwargs)

        self.representation = str()
        self.price_type_id = str()
        self.price_for_sku = Decimal()
        self.currency_name = str()
        self.sku_name = str()
        self.sku_ratio = Decimal()


class Offer(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Offer, self).__init__(*args, **kwargs)

        self.id = str()
        self.name = str()
        self.sku_id = str()
        self.prices = list()
        self.quantity = int()


class Client(BaseItem):

    def __init__(self):
        super().__init__()

        self.id = str()
        self.name = str()
        self.role = BUYER
        self.full_name = str()
        self.first_name = str()
        self.last_name = str()
        self.address = str()


class OrderItem(BaseItem):

    def __init__(self):
        super().__init__()

        self.id = str()
        self.name = str()
        self.sku = Sku(None)
        self.price = Decimal()
        self.quant = Decimal()
        self.sum = Decimal()


class Order(BaseItem):

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)

        self.id = str()
        self.number = str()
        self.date = datetime.now().date()
        self.currency_name = str()
        self.currency_rate = Decimal()
        self.operation = PRODUCT_ORDER
        self.role = SELLER
        self.sum = Decimal()
        self.client = Client()
        self.time = datetime.now().time()
        self.comment = str()
        self.items = list()
        self.additional_fields = list()
