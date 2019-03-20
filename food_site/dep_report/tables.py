import django_tables2 as tables
from sku_manage.models import Ingredient, ManufacturingLine

class IngredientTable(tables.Table):
	add = tables.TemplateColumn(orderable=False, verbose_name="Add", template_name='dep_report/addcolumn.html')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'add']

class SelectedTable(tables.Table):
	remove = tables.TemplateColumn(orderable=False, verbose_name="Remove", template_name='dep_report/remcolumn.html')
	class Meta:
		model = Ingredient
		fields = ['remove', 'name', 'number']

class MfgLineTable(tables.Table):
	view_column = tables.TemplateColumn(orderable=False, verbose_name="View Schedule", template_name='dep_report/viewcolumn.html')
	class Meta:
		model = ManufacturingLine
		fields = ['name', 'shortname']
