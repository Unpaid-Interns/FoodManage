import django_tables2 as tables
from .models import SalesRecord
from sku_manage.models import Ingredient, ManufacturingLine, ProductLine

class SkuSalesTable(tables.Table):
	year = tables.TemplateColumn('{% load ex_tags %}{{ record.date|year }}', order_by='date')
	week = tables.TemplateColumn('{% load ex_tags %}{{ record.date|week }}', orderable=False)
	customer_name = tables.TemplateColumn('{{ record.customer.name }}', orderable=False)
	customer_number = tables.TemplateColumn('{{ record.customer.number }}', orderable=False, verbose_name="Cust#")
	revenue = tables.TemplateColumn('{% load ex_tags %}{{ record.cases_sold|mult:record.price_per_case }}', orderable=False)
	class Meta:
		model = SalesRecord
		fields = ['year', 'week', 'customer_number', 'customer_name', 'cases_sold', 'price_per_case', 'revenue']

class ProductLineTable(tables.Table):
	add = tables.TemplateColumn(orderable=False, verbose_name="Add to Report", template_name='sales/addcolumn.html')
	class Meta:
		model = ProductLine
		fields = ['add', 'name']

class SelectedPLTable(tables.Table):
	remove = tables.TemplateColumn(orderable=False, verbose_name="Remove", template_name='sales/remcolumn.html')
	class Meta:
		model = ProductLine
		fields = ['name', 'remove']

class SkuSummaryTable(tables.Table):
	year = tables.Column()
	sku = tables.Column(verbose_name="SKU")
	revenue = tables.Column(verbose_name="Total Revenue")
	revenue_per_case = tables.Column(verbose_name="Average Revenue per Case")

class SkuTotalTable(tables.Table):
	revenue = tables.Column(verbose_name="Total Revenue")
	mfg_run_size = tables.Column(verbose_name="Avg Manufacturing Run Size")
	ingredient_cost = tables.Column(verbose_name="Ingr Cost / Case")
	mfg_setup_cost = tables.Column(verbose_name="Avg Manufacturing Setup Cost / Case")
	mfg_run_cost = tables.Column(verbose_name="Manufacturing Run Cost / Case")
	cogs = tables.Column(verbose_name="Total COGS / Case")
	revenue_per_case = tables.Column(verbose_name="Avg Revenue / Case")
	profit_per_case = tables.Column(verbose_name="Avg Profit / Case")
	profit_margin = tables.Column(verbose_name="Profit Margin")


