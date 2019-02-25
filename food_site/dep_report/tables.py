import django_tables2 as tables
from sku_manage.models import Ingredient, ManufacturingLine

class IngredientTable(tables.Table):
	add_colunm = tables.TemplateColumn(order_by='id', verbose_name="Add to Report", template_name='dep_report/addcolumn.html')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost']

class SelectedTable(tables.Table):
	remove_colunm = tables.TemplateColumn(order_by='id', verbose_name="Remove", template_name='dep_report/remcolumn.html')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost']

class MfgLineTable(tables.Table):
	view_column = tables.TemplateColumn(order_by='id', verbose_name="View Schedule", template_name='dep_report/viewcolumn.html')
	class Meta:
		model = ManufacturingLine
		fields = ['name', 'shortname']