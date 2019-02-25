import django_tables2 as tables
from sku_manage.models import SKU

class SKUTable(tables.Table):
	lines_column = tables.TemplateColumn(order_by='skumfgline', verbose_name="Manufacturing Lines", template_name='mfg_map/linecolumn.html')
	add_colunm = tables.TemplateColumn(order_by='id', verbose_name="Add", template_name='mfg_map/addcolumn.html')
	class Meta:
		model = SKU
		fields = ['name', 'sku_num']

class SelectedTable(tables.Table):
	lines_column = tables.TemplateColumn(order_by='skumfgline', verbose_name="Manufacturing Lines", template_name='mfg_map/linecolumn.html')
	remove_colunm = tables.TemplateColumn(order_by='id', verbose_name="Remove", template_name='mfg_map/remcolumn.html')
	class Meta:
		model = SKU
		fields = ['name', 'sku_num']
