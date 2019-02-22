import csv

from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from sku_manage.models import Ingredient, SKU
from django_tables2 import RequestConfig, paginators
from .tables import IngredientTable, SelectedTable

def ingr_dep_menu(request):
	if 'ingredients' not in request.session or request.session.get('ingredients') == None:
		request.session['ingredients'] = list()
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
	selected_set = Ingredient.objects.filter(id__in=request.session.get('ingredients'))
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

	input_table = IngredientTable(queryset)
	selected_table = SelectedTable(selected_set)
	context['input_table'] = input_table
	context['selected_table'] = selected_table
	RequestConfig(request, paginate=paginate).configure(input_table)
	return render(request, 'dep_report/data.html', context)

def ingr_dep_add(request, pk):
	ingredients = [pk]
	ingredients.extend(request.session.get('ingredients'))
	request.session['ingredients'] = ingredients
	return redirect('ingr_dep')

def ingr_dep_remove(request, pk):
	ingredients = list()
	ingredients.extend(request.session.get('ingredients'))
	ingredients.remove(pk)
	request.session['ingredients'] = ingredients
	return redirect('ingr_dep')

def ingr_dep_generate(request):
	return redirect('ingr_dep_report')

def ingr_dep_report(request):
	ingredients = Ingredient.objects.filter(id__in=request.session.get('ingredients'))
	context = {'ingredients': ingredients}
	return render(request, 'dep_report/detail.html', context)

def ingr_dep_download(request):
	ingredients = Ingredient.objects.filter(id__in=request.session.get('ingredients'))
	if request.method == 'POST' and 'download' in request.POST:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="report.csv"'
		writer = csv.writer(response)
		writer.writerow(['Ingredient', 'SKUs (SKU#: Name)'])
		for ingredient in ingredients.all():
			row = [str(ingredient)]
			for choice in ingredient.ingredientqty_set.all():
				for sku in choice.formula.sku_set.all():
					row.append(str(sku.sku_num) + ': ' + str(sku))
			writer.writerow(row)
		return response

