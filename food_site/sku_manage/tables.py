import django_tables2 as tables
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty

class IngredientTable(tables.Table):
	class Meta:
		model = Ingredient

class ProductLineTable(tables.Table):
	class Meta:
		model = ProductLine

class SKUTable(tables.Table):
	class Meta:
		model = SKU

class IngredientQtyTable(tables.Table):
	class Meta:
		model = SKU
