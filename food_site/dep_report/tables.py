import django_tables2 as tables
from sku_manage.models import Ingredient

class IngredientTable(tables.Table):
	add_colunm = tables.TemplateColumn(verbose_name="Add to Report", template_name='dep_report/addcolumn.html')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost']

class SelectedTable(tables.Table):
	remove_colunm = tables.TemplateColumn(verbose_name="Remove", template_name='dep_report/remcolumn.html')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost']