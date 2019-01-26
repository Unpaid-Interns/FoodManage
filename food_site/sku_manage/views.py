from django.shortcuts import render
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty
from django.views import generic

# Create your views here.
class IngredientView(generic.ListView):
	model = Ingredient
	template_name = 'sku_manage/data.html'
	def get_queryset(self):
		return Ingredient.objects.all()

class ProductLineView(generic.ListView):
	model = ProductLine
	template_name = 'sku_manage/data.html'
	def get_queryset(self):
		return ProductLine.objects.all()

class SKUView(generic.ListView):
	model = SKU
	template_name = 'sku_manage/data.html'
	def get_queryset(self):
		return SKU.obkects.all()

class IngredientQtyView(generic.ListView):
	model = IngredientQty
	template_name = 'sku_manage/data.html'
	def get_queryset(self):
		return IngredientQty.objects.all()

def data(request):
	return render(request, 'sku_manage/data.html', context=None)

	
