import csv

from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import HttpResponse
from sku_manage.models import Ingredient, SKU, ManufacturingLine, IngredientQty
from django_tables2 import RequestConfig, paginators
from .tables import IngredientTable, SelectedTable, MfgLineTable
from manufacturing_goals.models import ScheduleItem
from manufacturing_goals import unitconvert

@login_required
def reporting(request):
	return render(request, 'dep_report/reporting.html', context=None)

@permission_required('sku_manage.report_ingredient')
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
	queryset = queryset.exclude(id__in=request.session.get('ingredients'))
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
				queryset = queryset.filter(ingredientqty__formula__sku__sku_num=sku_num)
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

@permission_required('sku_manage.report_ingredient')
def ingr_dep_add(request, pk):
	ingredients = [pk]
	ingredients.extend(request.session.get('ingredients'))
	request.session['ingredients'] = ingredients
	return redirect('ingr_dep')

@permission_required('sku_manage.report_ingredient')
def ingr_dep_remove(request, pk):
	ingredients = list()
	ingredients.extend(request.session.get('ingredients'))
	ingredients.remove(pk)
	request.session['ingredients'] = ingredients
	return redirect('ingr_dep')

@permission_required('sku_manage.report_ingredient')
def ingr_dep_generate(request):
	return redirect('ingr_dep_report')

@permission_required('sku_manage.report_ingredient')
def ingr_dep_report(request):
	ingredients = Ingredient.objects.filter(id__in=request.session.get('ingredients'))
	context = {'ingredients': ingredients}
	return render(request, 'dep_report/detail.html', context)

@permission_required('sku_manage.report_ingredient')
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

@permission_required('sku_manage.report_manufacturingline')
def mfg_sch_menu(request):
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

	table = MfgLineTable(queryset)
	context['table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'dep_report/select.html', context)

@permission_required('sku_manage.report_manufacturingline')
def schedule_report(request, pk):
	manufacturingline = ManufacturingLine.objects.get(pk=pk)
	schedule_items = ScheduleItem.objects.filter(mfgline=manufacturingline, mfgqty__goal__enabled=True, start__isnull=False).order_by('start')
	if request.method == 'GET':
		if 'starttime' in request.GET and request.GET['starttime'] != '':
			start_time = request.GET['starttime']
			schedule_items = schedule_items.filter(start__gte=start_time)
		if 'endtime' in request.GET and request.GET['endtime'] != '':
			end_time = request.GET['endtime']
			schedule_items = schedule_items.filter(start__lt=end_time)			

	ingredient_list = Ingredient.objects.filter(ingredientqty__formula__sku__manufacturingqty__scheduleitem__in=schedule_items)
	ingredient_dict = dict()
	for ingredient in ingredient_list:
		total_q = 0
		for schedule_item in schedule_items:
			sku = schedule_item.mfgqty.sku
			caseqty = schedule_item.mfgqty.caseqty
			ingrqty = IngredientQty.objects.get(formula__sku=sku, ingredient=ingredient)
			quantity = round(ingrqty.quantity * caseqty * sku.formula_scale, 12)
			total_q += unitconvert.convert(quantity, ingrqty.quantity_units, ingredient.package_size_units)
		package_num = round(total_q / ingredient.package_size, 12)
		ingredient_dict[ingredient] = [total_q, package_num]

	context = {
		'manufacturingline': manufacturingline,
		'schedule_items': schedule_items,
		'ingredients': ingredient_dict,
	}
	return render(request, 'dep_report/schedule_detail.html', context)
