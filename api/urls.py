from django.urls import re_path
from . import views

app_name = 'api'

urlpatterns = [
    re_path(r'^properties/$', views.api_properties, name='properties'),
    re_path(r'^properties/(?P<pk>\d+)/$', views.api_property_detail, name='property_detail'),
    re_path(r'^statistics/$', views.api_statistics, name='statistics'),
    re_path(r'^my-deals/$', views.api_my_deals, name='my_deals'),
]
