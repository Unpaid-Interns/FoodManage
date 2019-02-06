import django_tables2 as tables
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty

class IngredientTable(tables.Table):
	name = tables.TemplateColumn('<a class="ing" href="{{record.pk}}">{{ record.name }}</a>')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost', 'comment', 'skus']

class ProductLineTable(tables.Table):
	name = tables.TemplateColumn('<a class="ing" href="{{record.pk}}">{{ record.name }}</a>')
	class Meta:
		model = ProductLine
		fields = ['name', 'skus']

class SKUTable(tables.Table):
	name = tables.TemplateColumn('<a class="ing" href="{{record.pk}}">{{ record.name }}</a>')
	class Meta:
		model = SKU
		fields = ['name', 'sku_num', 'case_upc', 'unit_upc', 'unit_size', 'units_per_case', 'product_line', 'comment', 'ingredients']

class IngredientQtyTable(tables.Table):
	class Meta:
		model = IngredientQty
		fields = ['sku', 'ingredient', 'quantity']
