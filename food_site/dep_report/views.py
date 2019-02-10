import csv

from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from sku_manage.models import Ingredient, SKU
from django_tables2 import RequestConfig, paginators
from sku_manage.tables import IngredientTable

def ingr_dep_menu(request):
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
	if 'sort' in request.GET:
		request.session['choices'] = queryset.order_by(request.GET['sort']).values_list('id', flat=True)
	else:
		request.session['choices'] = list(queryset.values_list('id', flat=True))
	table = IngredientTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'dep_report/data.html', context)

def ingr_dep_report(request):
	choices = request.session.get('choices')
	ingredients = Ingredient.objects.filter(id__in=choices)

	if request.method == 'POST' and 'download' in request.POST:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="report.csv"'
		writer = csv.writer(response)
		writer.writerow(['Ingredient', 'SKUs'])
		for ingredient in ingredients.all():
			row = [str(ingredient)]
			for choice in ingredient.ingredientqty_set.all():
				row.append(str(choice.sku))
			writer.writerow(row)
		return response

	context = {'ingredients': ingredients}
	return render(request, 'dep_report/detail.html', context)
