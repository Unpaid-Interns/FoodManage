import django_filters
from sku_manage.models import Ingredient


class IngredientFilter(django_filters.FilterSet):
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost', 'comment']
