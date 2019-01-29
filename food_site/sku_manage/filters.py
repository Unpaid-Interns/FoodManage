import django_filters
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty

class IngredientFilter(django_filters.FilterSet):
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost', 'comment']

class ProductLineFilter(django_filters.FilterSet):
	class Meta:
		model = ProductLine
		fields = ['name']

class SKUFilter(django_filters.FilterSet):
	class Meta:
		model = SKU
		fields = ['name', 'sku_num', 'case_upc', 'unit_upc', 'unit_size', 'units_per_case', 'product_line', 'comment']

class IngredientQtyFilter(django_filters.FilterSet):
	class Meta:
		model = IngredientQty
		fields = ['sku', 'ingredient', 'quantity']
