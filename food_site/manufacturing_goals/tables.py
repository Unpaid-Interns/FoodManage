import django_tables2 as tables
from sku_manage.models import SKU
from .models import ManufacturingQty, ManufacturingGoal

class SKUTable(tables.Table):
	add = tables.TemplateColumn(orderable=False, verbose_name="Add", template_name='manufacturing_goals/addcolumn.html')
	class Meta:
		model = SKU
		fields = ['name', 'sku_num', 'add']

class MfgQtyTable(tables.Table):
	remove = tables.TemplateColumn(orderable=False, verbose_name="Remove", template_name='manufacturing_goals/remcolumn.html')
	caseqty = tables.Column(verbose_name="Case Qty")
	class Meta:
		model = ManufacturingQty
		fields = ['sku', 'caseqty', 'remove']

class EnableTable(tables.Table):
	name = tables.TemplateColumn(template_name='manufacturing_goals/goalnamecolumn.html')
	enable = tables.TemplateColumn(orderable=False, verbose_name="Action", template_name='manufacturing_goals/enablecolumn.html')
	class Meta:
		model = ManufacturingGoal
		fields = [ 'name', 'user', 'last_edit', 'deadline', 'enable']
