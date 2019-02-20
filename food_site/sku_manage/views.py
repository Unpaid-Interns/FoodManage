from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import RequestConfig, paginators
from exporter import CSVExport
from .models import Ingredient, ProductLine, SKU, Formula, ManufacturingLine
from .tables import IngredientTable, ProductLineTable, SKUTable, FormulaTable, ManufacturingLineTable

@login_required
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
				Q(package_size__iexact=keyword) | 
				Q(cost__iexact=keyword) | 
				Q(comment__icontains=keyword))
			context['keyword'] = keyword

		if 'skufilter' in request.GET:
			sku_num = request.GET['skufilter']
			if sku_num != 'all':
				queryset = queryset.filter(ingredientqty__formula__sku__sku_num=sku_num)
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

@method_decorator(login_required, name='dispatch')
class IngredientDetailView(generic.DetailView):
	model = Ingredient
	template_name = 'sku_manage/ingredient_detail.html'

	def get_fields(self):
		return [(key, value) for key, value in self.__dict__.items()]

@login_required
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
				queryset = queryset.filter(sku__sku_num=sku_num)
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

@method_decorator(login_required, name='dispatch')
class ProductLineDetailView(generic.DetailView):
	model = ProductLine
	template_name = 'sku_manage/product_line_detail.html'

@login_required
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
				queryset = queryset.filter(formula__ingredientqty__ingredient__number=ingr_num)
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

@method_decorator(login_required, name='dispatch')
class SKUDetailView(generic.DetailView):
	model = SKU
	template_name = 'sku_manage/sku_detail.html'

@login_required(login_url='index')
def FormulaView(request):
	queryset = Formula.objects.all()
	context = {
		'paginated': True,
		'keyword': '',
		'all_ingredients': Ingredient.objects.all(),
		'selected_ingredient': None,
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
			queryset = queryset.filter(Q(name__icontains=keyword) | 
				Q(number__iexact=keyword) |
				Q(comment__icontains=keyword))
			context['keyword'] = keyword

		if 'ingredientfilter' in request.GET:
			ingr_num = request.GET['ingredientfilter']
			if ingr_num != 'all':
				queryset = queryset.filter(ingredientqty__ingredient__number=ingr_num)
				context['selected_ingredient'] = int(ingr_num)

		if 'skufilter' in request.GET:
			sku_num = request.GET['skufilter']
			if sku_num != 'all':
				queryset = queryset.filter(sku__sku_num=sku_num)
				context['selected_sku'] = int(sku_num)

		if 'remove_pagination' in request.GET:
			paginate = False
			context['paginated'] = False

	if request.method == 'POST' and 'export_data' in request.POST:
		if 'sort' in request.GET:
			queryset = queryset.order_by(request.GET['sort']) 
		return CSVExport.export_to_csv('formulas', queryset)

	table = FormulaTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

@method_decorator(login_required, name='dispatch')
class FormulaDetailView(generic.DetailView):
	model = Formula
	template_name = 'sku_manage/formula_detail.html'

@login_required
def ManufacturingLineView(request):
	queryset = ManufacturingLine.objects.all()
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
			queryset = queryset.filter(Q(name__icontains=keyword) | 
				Q(shortname__icontains=keyword) |
				Q(comment__icontains=keyword))
			context['keyword'] = keyword

		if 'skufilter' in request.GET:
			sku_num = request.GET['skufilter']
			if sku_num != 'all':
				queryset = queryset.filter(skumfgline__sku__sku_num=sku_num)
				context['selected_sku'] = int(sku_num)

		if 'remove_pagination' in request.GET:
			paginate = False
			context['paginated'] = False

	if request.method == 'POST' and 'export_data' in request.POST:
		if 'sort' in request.GET:
			queryset = queryset.order_by(request.GET['sort']) 
		return CSVExport.export_to_csv('manufacturing_lines', queryset)

	table = ManufacturingLineTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'sku_manage/data.html', context)

@method_decorator(login_required, name='dispatch')
class ManufacturingLineDetailView(generic.DetailView):
	model = ManufacturingLine
	template_name = 'sku_manage/mfg_line_detail.html'

@login_required
def search(request):
	return render(request, 'sku_manage/search.html', context=None)

@login_required
def authout(request):
        logout(request)
        response = redirect('/')
        return response

	
