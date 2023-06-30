import os
from collections import defaultdict

from appconf import AppConf
from django.conf import settings

__all__ = (
    'settings',
    'CMLAppConf',
)


class CMLAppConf(AppConf):
    RESPONSE_SUCCESS = 'success'
    RESPONSE_PROGRESS = 'progress'
    RESPONSE_ERROR = 'failure'

    MAX_EXEC_TIME = 60
    USE_ZIP = False
    FILE_LIMIT = 0

    UPLOAD_ROOT = os.path.join(settings.MEDIA_ROOT, 'cml', 'tmp')

    DELETE_FILES_AFTER_IMPORT = True

    DOC_MAJOR_VER = 2
    DOC_MINOR_VER = 1
    DOC_VERSION = f'{DOC_MAJOR_VER}.{DOC_MINOR_VER}'
    DOC_XMLNS = f'urn:1C.ru:commerceml_{DOC_MAJOR_VER}_{DOC_MINOR_VER}'

    DEFAULT_CHARSET = 'windows-1251'

    CATALOG_FILE_DOWNLOAD_PATH = defaultdict(
        lambda: getattr(settings, 'CML_UPLOAD_ROOT'),
        **{
            '.xml': UPLOAD_ROOT,
            '.png': settings.MEDIA_ROOT,
            '.jpeg': settings.MEDIA_ROOT,
            '.jpg': settings.MEDIA_ROOT,
        })
    TEMP_FILE_CONTENT_TYPE = defaultdict(
        lambda: f'application/xml;charset={getattr(settings, "CML_DEFAULT_CHARSET")}',
        **{
            '.xml': f'application/xml;charset={DEFAULT_CHARSET}',
            '.png': 'image/png',
            '.jpeg': 'image/jpeg',
            '.jpg': 'image/jpg',
        })
