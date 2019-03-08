import django_tables2 as tables
from .models import SalesRecord
from sku_manage.models import Ingredient, ManufacturingLine

class SkuSalesTable(tables.Table):
	year = tables.TemplateColumn('{% load ex_tags %}{{ record.date|year }}', order_by='date')
	week = tables.TemplateColumn('{% load ex_tags %}{{ record.date|week }}', orderable=False)
	customer_name = tables.TemplateColumn('{{ record.customer.name }}', orderable=False)
	customer_number = tables.TemplateColumn('{{ record.customer.number }}', orderable=False, verbose_name="Cust#")
	revenue = tables.TemplateColumn('{% load ex_tags %}{{ record.cases_sold|mult:record.price_per_case }}', orderable=False)
	class Meta:
		model = SalesRecord
		fields = ['year', 'week', 'customer_number', 'customer_name', 'cases_sold', 'price_per_case', 'revenue']
