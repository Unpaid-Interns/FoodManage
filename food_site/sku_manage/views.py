from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import logout
from django_tables2 import RequestConfig, paginators
from .models import Ingredient, ProductLine, SKU, IngredientQty
from .tables import IngredientTable, ProductLineTable, SKUTable, IngredientQtyTable
from .filters import IngredientFilter, ProductLineFilter, SKUFilter, IngredientQtyFilter 

# Create your views here.
def IngredientView(request):
	queryset = Ingredient.objects.all()
	f = IngredientFilter(request.GET, queryset=queryset)
	table = IngredientTable(f.qs)

	context = {
		'table': table, 
		'filter': f, 
		'paginated': True,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25
	}
	if request.method == 'GET' and 'remove_pagination' in request.GET:
		print(request.GET)
		paginate = False
		context['paginated'] = False

	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

class IngredientDetailView(generic.DetailView):
	model = Ingredient
	template_name = 'sku_manage/ingredient_detail.html'

	def get_fields(self):
		return [(key, value) for key, value in self.__dict__.items()]


def ProductLineView(request):
	queryset = ProductLine.objects.all()
	f = ProductLineFilter(request.GET, queryset=queryset)
	table = ProductLineTable(f.qs)

	context = {
		'table': table, 
		'filter': f, 
		'paginated': True,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25
	}
	if request.method == 'GET' and 'remove_pagination' in request.GET:
		print(request.GET)
		paginate = False
		context['paginated'] = False


	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

class ProductLineDetailView(generic.DetailView):
	model = ProductLine
	template_name = 'sku_manage/product_line_detail.html'

def SKUView(request):
	queryset = SKU.objects.all()
	f = SKUFilter(request.GET, queryset=queryset)
	table = SKUTable(f.qs)

	context = {
		'table': table, 
		'filter': f, 
		'paginated': True,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25
	}
	if request.method == 'GET' and 'remove_pagination' in request.GET:
		print(request.GET)
		paginate = False
		context['paginated'] = False

	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

class SKUDetailView(generic.DetailView):
	model = SKU
	template_name = 'sku_manage/sku_detail.html'

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

	
