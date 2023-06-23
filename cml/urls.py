from __future__ import absolute_import

from django.conf.urls import include
from django.urls import path

from . import views

app_urlpatterns = (
    path('1c_exchange.php', views.front_view, name='front_view'),
    path('exchange/', views.front_view, name='front_view')
)

urlpatterns = (
    path('/', include((app_urlpatterns, 'cml'), namespace='cml')),
)
