import django_tables2 as tables
from sku_manage.models import Ingredient


class IngredientTable(tables.Table):
	name = tables.TemplateColumn('''
			<input type="checkbox" name="choice" id="choice"{{ record.pk }} value="{{ record.pk }}">
			<label for="choice{{ record.pk }}">{{ record.name }}</label><br>
		''')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost', 'comment']