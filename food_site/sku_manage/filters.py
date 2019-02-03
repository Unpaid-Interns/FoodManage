import django_filters
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty


class IngredientFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(lookup_expr='icontains')
	skus = django_filters.ModelChoiceFilter(queryset=SKU.objects.all(), field_name='ingredientqty__sku')
	vendor_info = django_filters.CharFilter(lookup_expr='icontains')
	package_size = django_filters.CharFilter(lookup_expr='icontains')
	comment = django_filters.CharFilter(lookup_expr='icontains')
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost', 'comment']

class ProductLineFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(lookup_expr='icontains')
	skus = django_filters.ModelChoiceFilter(queryset=SKU.objects.all(), field_name='sku')
	class Meta:
		model = ProductLine
		fields = ['name']

class SKUFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(lookup_expr='icontains')
	ingredients = django_filters.ModelChoiceFilter(queryset=Ingredient.objects.all(), field_name='ingredientqty__ingredient')
	unit_size = django_filters.CharFilter(lookup_expr='icontains')
	comment = django_filters.CharFilter(lookup_expr='icontains')
	class Meta:
		model = SKU
		fields = ['name', 'sku_num', 'case_upc', 'unit_upc', 'unit_size', 'units_per_case', 'product_line', 'comment']

class IngredientQtyFilter(django_filters.FilterSet):
	class Meta:
		model = IngredientQty
		fields = ['sku', 'ingredient', 'quantity']
