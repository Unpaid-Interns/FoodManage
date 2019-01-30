from django.shortcuts import render
from django.views import generic
from .models import Ingredient
from .models import ProductLine
from .models import SKU
from .models import IngredientQty
from django.views import generic
from django.contrib.auth import logout
from django.shortcuts import redirect
from django_tables2 import RequestConfig
from .tables import IngredientTable
from .tables import ProductLineTable
from .tables import SKUTable
from .tables import IngredientQtyTable
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from .filters import IngredientFilter
from .filters import ProductLineFilter
from .filters import SKUFilter
from .filters import IngredientQtyFilter 

# Create your views here.
def IngredientView(request):
	queryset = Ingredient.objects.all()
	f = IngredientFilter(request.GET, queryset=queryset)
	table = IngredientTable(f.qs)
	RequestConfig(request, paginate={'per_page': 25}).configure(table)
	return render(request, 'sku_manage/data.html', {'table': table, 'filter': f})

class IngredientDetailView(generic.DetailView):
	model = Ingredient
	template_name = sku_manage/ingredient_detail.html


def ProductLineView(request):
	queryset = ProductLine.objects.all()
	f = ProductLineFilter(request.GET, queryset=queryset)
	table = ProductLineTable(f.qs)
	RequestConfig(request, paginate={'per_page': 25}).configure(table)
	return render(request, 'sku_manage/data.html', {'table': table, 'filter': f})

def SKUView(request):
	queryset = SKU.objects.all()
	f = SKUFilter(request.GET, queryset=queryset)
	table = SKUTable(f.qs)
	RequestConfig(request, paginate={'per_page': 25}).configure(table)
	return render(request, 'sku_manage/data.html', {'table': table, 'filter': f})

class SKUDetailView(generic.DetailView):
	model = SKU
	template_name = sku_manage/sku_detail.html

def IngredientQtyView(request):
	queryset = IngredientQty.objects.all()
	f = IngredientQtyFilter(request.GET, queryset=queryset)
	table = IngredientQtyTable(f.qs)
	RequestConfig(request, paginate={'per_page': 25}).configure(table)
	return render(request, 'sku_manage/data.html', {'table': table, 'filter': f})

def search(request):
	return render(request, 'sku_manage/search.html', context=None)

def authout(request):
        logout(request)
        response = redirect('/')
        return response

	
