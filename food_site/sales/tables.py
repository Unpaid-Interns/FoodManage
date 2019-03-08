import django_tables2 as tables
from .models import SalesRecord
from sku_manage.models import Ingredient, ManufacturingLine

class SkuSalesTable(tables.Table):
	customer_name = tables.TemplateColumn('{{ record.customer.name }}', orderable=False)
	customer_number = tables.TemplateColumn('{{ record.customer.number }}', orderable=False)
	class Meta:
		model = SalesRecord
		fields = ['date', 'customer_name', 'customer_number', 'cases_sold', 'price_per_case']
