from django.shortcuts import render
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django_tables2 import RequestConfig
from .tables import IngredientTable
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from .filters import IngredientFilter

# Create your views here.
def IngredientView(request):
	queryset = Ingredient.objects.all()
	f = IngredientFilter(request.GET, queryset=queryset)
	table = IngredientTable(f.qs)
	RequestConfig(request, paginate={'per_page': 25}).configure(table)
	return render(request, 'sku_manage/ingredient.html', {'table': table, 'filter': f})

class FilteredIngredientView(SingleTableMixin, FilterView):
	table_class = IngredientTable
	model = Ingredient
	template_name = 'sku_manage/ingredient.html'

class ProductLineView(generic.ListView):
	model = ProductLine
	template_name = 'sku_manage/productline.html'
	context_object_name = 'ProductLine_list'
	def get_queryset(self):
		return ProductLine.objects.all()

class SKUView(generic.ListView):
	model = SKU
	template_name = 'sku_manage/sku.html'
	context_object_name = 'SKU_list'
	def get_queryset(self):
		return SKU.objects.all()

class IngredientQtyView(generic.ListView):
	model = IngredientQty
	template_name = 'sku_manage/ingredientqty.html'
	context_object_name = 'IngredientQty_list'
	def get_queryset(self):
		return IngredientQty.objects.all()

def search(request):
	return render(request, 'sku_manage/search.html', context=None)

def authout(request):
        logout(request)
        response = redirect('/')
        return response


	
