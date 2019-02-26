import django_tables2 as tables
from sku_manage.models import SKU
from .models import ManufacturingQty, ManufacturingGoal

class SKUTable(tables.Table):
	add_colunm = tables.TemplateColumn(orderable=False, verbose_name="Add", template_name='manufacturing_goals/addcolumn.html')
	class Meta:
		model = SKU
		fields = ['name', 'sku_num', 'case_upc']

class MfgQtyTable(tables.Table):
	remove_colunm = tables.TemplateColumn(orderable=False, verbose_name="Remove", template_name='manufacturing_goals/remcolumn.html')
	class Meta:
		model = ManufacturingQty
		fields = ['sku', 'caseqty']

class EnableTable(tables.Table):
	enable = tables.TemplateColumn(orderable=False, verbose_name="Action", template_name='manufacturing_goals/enablecolumn.html')
	class Meta:
		model = ManufacturingGoal
		fields = [ 'name', 'user.name', 'deadline']
