# dep_report/urls.py
from django.conf.urls import url
from django.urls import path
from . import views
from . import tasks
from django.utils import timezone
from datetime import timedelta
from background_task.models import Task

urlpatterns = [
	path('sales/report/<int:pk>/', views.sku_drilldown, name='sku_drilldown'),
	path('sales/', views.pl_select, name='sales_report_select'),
	path('sales/add/<int:pk>/', views.product_line_add, name='sales_product_line_add'),
	path('sales/remove/<int:pk>/', views.product_line_remove, name='sales_product_line_remove'),
	path('sales/report/', views.sales_report, name='sales_report'),
	path('scrape/', views.scrape, name='scrape'),
]

# Initialize Scraping
Task.objects.filter(repeat=86400).delete()
tasks.scrape_year(repeat=86400, schedule=timezone.now().replace(hour=7, minute=0, second=0) + timedelta(days=1))
