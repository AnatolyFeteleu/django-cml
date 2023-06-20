from __future__ import absolute_import

from django.conf import settings
from django.db import models


class Exchange(models.Model):

    class ExchangeType(models.TextChoices):
        IMPORT = 'import', 'Импорт'
        EXPORT = 'export', 'Экспорт'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exchange_type = models.CharField(max_length=50, choices=ExchangeType.choices)
    filename = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Exchange log entry'
        verbose_name_plural = 'Exchange log entries'

    @classmethod
    def log(cls, exchange_type, user, filename=str()):
        ex_log = Exchange(
            exchange_type=exchange_type,
            user=user,
            filename=filename
        )
        ex_log.save()
