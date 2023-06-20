import os

from appconf import AppConf
from django.conf import settings


class CMLAppCong(AppConf):

    RESPONSE_SUCCESS = 'success'
    RESPONSE_PROGRESS = 'progress'
    RESPONSE_ERROR = 'failure'

    MAX_EXEC_TIME = 60
    USE_ZIP = False
    FILE_LIMIT = 0

    UPLOAD_ROOT = os.path.join(settings.MEDIA_ROOT, 'cml', 'tmp')

    DELETE_FILES_AFTER_IMPORT = True

    MAJOR_VERSION = 2
    MINOR_VERSION = 1
    VERSION = f'{MAJOR_VERSION}.{MINOR_VERSION}'
    XMLNS = f'urn:1C.ru:commerceml_{MAJOR_VERSION}_{MINOR_VERSION}'
