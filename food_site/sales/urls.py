# dep_report/urls.py
from django.conf.urls import url
from django.urls import path
from . import views
from . import tasks

urlpatterns = [
	path('sales/sku/<int:pk>/', views.sku_drilldown, name='sku_drilldown'),
	path('sales/productline/', views.pl_select, name='sales_report_select'),
	path('sales/productline/add/<int:pk>/', views.product_line_add, name='sales_product_line_add'),
	path('sales/productline/remove/<int:pk>/', views.product_line_remove, name='sales_product_line_remove'),
	path('sales/report/', views.sales_report, name='sales_report'),
	path('scrape/', views.scrape, name='scrape'),
]

tasks.scrape(repeat=86400)
