import django_filters
from .models import Ingredient

class IngredientFilter(django_filters.FilterSet):
	class Meta:
		model = Ingredient
		fields = ['name', 'number', 'vendor_info', 'package_size', 'cost', 'comment']
