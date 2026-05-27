from django.urls import re_path
from . import views, multitasking_views

app_name = 'properties'

urlpatterns = [
    # Главная и общие страницы
    re_path(r'^$', views.home, name='home'),
    re_path(r'^about/$', views.about, name='about'),
    re_path(r'^news/$', views.news_list, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),
    re_path(r'^glossary/$', views.glossary, name='glossary'),
    re_path(r'^contacts/$', views.contacts, name='contacts'),
    re_path(r'^privacy/$', views.privacy, name='privacy'),
    re_path(r'^vacancies/$', views.vacancies, name='vacancies'),
    re_path(r'^reviews/$', views.reviews, name='reviews'),
    re_path(r'^promos/$', views.promo_codes, name='promos'),

    # Объекты недвижимости
    re_path(r'^properties/$', views.property_list, name='list'),
    re_path(r'^properties/(?P<pk>\d+)/$', views.property_detail, name='detail'),
    re_path(r'^properties/create/$', views.property_create, name='create'),
    re_path(r'^properties/(?P<pk>\d+)/edit/$', views.property_update, name='update'),
    re_path(r'^properties/(?P<pk>\d+)/delete/$', views.property_delete, name='delete'),

    # Сделки
    re_path(r'^deals/$', views.deal_list, name='deal_list'),
    re_path(r'^deals/create/$', views.deal_create, name='deal_create'),
    re_path(r'^deals/(?P<pk>\d+)/edit/$', views.deal_update, name='deal_update'),
    re_path(r'^deals/(?P<pk>\d+)/delete/$', views.deal_delete, name='deal_delete'),

    # Клиенты
    re_path(r'^clients/$', views.client_list, name='client_list'),
    re_path(r'^clients/create/$', views.client_create, name='client_create'),
    re_path(r'^clients/(?P<pk>\d+)/edit/$', views.client_update, name='client_update'),
    re_path(r'^clients/(?P<pk>\d+)/delete/$', views.client_delete, name='client_delete'),

    # Статистика
    re_path(r'^statistics/$', views.statistics, name='statistics'),
    re_path(r'^statistics/chart/$', views.chart_python, name='chart_python'),

    # Дополнительное задание — многозадачность
    re_path(r'^multitasking/$', multitasking_views.multitasking_demo, name='multitasking'),
]
