# dep_report/urls.py
from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
	path('sales/sku/<int:pk>/', views.sku_drilldown, name='sku_drilldown'),
]
