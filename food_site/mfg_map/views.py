from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from sku_manage.models import SKU, Ingredient, ProductLine, ManufacturingLine, SkuMfgLine
from django_tables2 import RequestConfig, paginators
from .tables import SKUTable, SelectedTable

def map_view(request):
	if 'skus' not in request.session or request.session.get('skus') == None:
		request.session['skus'] = list()
	queryset = SKU.objects.all()
	context = {
		'paginated': True,
		'keyword': '',
		'mfg_lines': ManufacturingLine.objects.all(),
		'all_ingredients': Ingredient.objects.all(),
		'selected_ingredient': None,
		'all_product_lines': ProductLine.objects.all(),
		'selected_product_line': None,
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25,
	}
	selected_set = SKU.objects.filter(id__in=request.session.get('skus'))
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

	input_table = SKUTable(queryset)
	selected_table = SelectedTable(selected_set)
	context['input_table'] = input_table
	context['selected_table'] = selected_table
	RequestConfig(request, paginate=paginate).configure(input_table)
	return render(request, 'mfg_map/data.html', context)

def map_add(request, pk):
	skus = [pk]
	skus.extend(request.session.get('skus'))
	request.session['skus'] = skus
	return redirect('map_view')

def map_remove(request, pk):
	skus = list()
	skus.extend(request.session.get('skus'))
	skus.remove(pk)
	request.session['skus'] = skus
	return redirect('map_view')

def edit_mapping(request):
	skus = SKU.objects.filter(id__in=request.session.get('skus'))
	op_type = request.POST['mfg-line-op']
	line_pk = int(request.POST['mfg-line-select'])
	if op_type == 'add':
		mfg_line = ManufacturingLine.objects.filter(id=line_pk)[0]
		for sku in skus:
			SkuMfgLine(sku=sku, mfg_line=mfg_line).save()
	else:
		SkuMfgLine.objects.filter(sku__in=skus, mfg_line__pk=line_pk).delete()
	return redirect('map_view')

