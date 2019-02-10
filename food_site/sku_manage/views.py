from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from django.contrib.auth import logout
from django_tables2 import RequestConfig, paginators
from exporter import CSVExport
from .models import Ingredient, ProductLine, SKU, IngredientQty
from .tables import IngredientTable, ProductLineTable, SKUTable, IngredientQtyTable

# Create your views here.
def IngredientView(request):
	queryset = Ingredient.objects.all()
	context = {
		'paginated': True,
		'keyword': '',
		'all_skus': SKU.objects.all(),
		'selected_sku': None,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25,
	}

	if request.method == 'GET':
		if 'keyword' in request.GET:
			keyword = request.GET['keyword']
			queryset = queryset.filter(Q(name__icontains=keyword) | 
				Q(number__iexact=keyword) |
				Q(vendor_info__icontains=keyword) | 
				Q(package_size__icontains=keyword) | 
				Q(cost__iexact=keyword) | 
				Q(comment__icontains=keyword))
			context['keyword'] = keyword

		if 'skufilter' in request.GET:
			sku_num = request.GET['skufilter']
			if sku_num != 'all':
				queryset = queryset.filter(ingredientqty__sku__sku_num=sku_num)
				context['selected_sku'] = int(sku_num)

		if 'remove_pagination' in request.GET:
			paginate = False
			context['paginated'] = False

	if request.method == 'POST' and 'export_data' in request.POST:
		if 'sort' in request.GET:
			queryset = queryset.order_by(request.GET['sort']) 
		return CSVExport.export_to_csv('ingredients', queryset)

	table = IngredientTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

class IngredientDetailView(generic.DetailView):
	model = Ingredient
	template_name = 'sku_manage/ingredient_detail.html'

	def get_fields(self):
		return [(key, value) for key, value in self.__dict__.items()]


def ProductLineView(request):
	queryset = ProductLine.objects.all()
	context = {
		'paginated': True,
		'keyword': '',
		'all_skus': SKU.objects.all(),
		'selected_sku': None,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25
	}

	if request.method == 'GET':
		if 'keyword' in request.GET:
			keyword = request.GET['keyword']
			queryset = queryset.filter(name__icontains=keyword)
			context['keyword'] = keyword

		if 'skufilter' in request.GET:
			sku_num = request.GET['skufilter']
			if sku_num != 'all':
				queryset = queryset.filter(ingredientqty__sku__sku_num=sku_num)
				context['selected_sku'] = int(sku_num)

		if 'remove_pagination' in request.GET:
			paginate = False
			context['paginated'] = False

	if request.method == 'POST' and 'export_data' in request.POST:
		if 'sort' in request.GET:
			queryset = queryset.order_by(request.GET['sort']) 
		return CSVExport.export_to_csv('product_lines', queryset)

	table = ProductLineTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

class ProductLineDetailView(generic.DetailView):
	model = ProductLine
	template_name = 'sku_manage/product_line_detail.html'

def SKUView(request):
	queryset = SKU.objects.all()
	context = {
		'paginated': True,
		'keyword': '',
		'all_ingredients': Ingredient.objects.all(),
		'selected_ingredient': None,
		'all_product_lines': ProductLine.objects.all(),
		'selected_product_line': None,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25
	}

	if request.method == 'GET':
		if 'keyword' in request.GET:
			keyword = request.GET['keyword']
			queryset = queryset.filter(Q(name__icontains=keyword) | 
				Q(sku_num__iexact=keyword) |
				Q(case_upc__iexact=keyword) |
				Q(unit_upc__iexact=keyword) |
				Q(unit_size__icontains=keyword) | 
				Q(units_per_case__iexact=keyword) | 
				Q(comment__icontains=keyword))
			context['keyword'] = keyword

		if 'ingredientfilter' in request.GET:
			ingr_num = request.GET['ingredientfilter']
			if ingr_num != 'all':
				queryset = queryset.filter(ingredientqty__ingredient__number=ingr_num)
				context['selected_ingredient'] = int(ingr_num)

		if 'productlinefilter' in request.GET:
			pl_name = request.GET['productlinefilter']
			if pl_name != 'all':
				queryset = queryset.filter(product_line__name=pl_name)
				context['selected_product_line'] = pl_name

		if 'remove_pagination' in request.GET:
			paginate = False
			context['paginated'] = False

	if request.method == 'POST' and 'export_data' in request.POST:
		if 'sort' in request.GET:
			queryset = queryset.order_by(request.GET['sort']) 
		return CSVExport.export_to_csv('skus', queryset)

	table = SKUTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

class SKUDetailView(generic.DetailView):
	model = SKU
	template_name = 'sku_manage/sku_detail.html'

def IngredientQtyView(request):
	queryset = IngredientQty.objects.all()
	f = IngredientQtyFilter(request.GET, queryset=queryset)
	table = IngredientQtyTable(f.qs)
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
		paginate = False
		context['paginated'] = False

	if request.method == 'POST' and 'export_data' in request.POST:
		qs = f.qs
		if 'sort' in request.GET:
			qs = f.qs.order_by(request.GET['sort']) 
		return CSVExport.export_to_csv('formulas', qs)

	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

def search(request):
	return render(request, 'sku_manage/search.html', context=None)

def authout(request):
        logout(request)
        response = redirect('/')
        return response

	
