import os

from django.conf import settings
from appconf import AppConf


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
