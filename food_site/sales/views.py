from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django_tables2 import RequestConfig, paginators
from sku_manage.models import SKU, ProductLine
from .models import SalesRecord, Customer
from .tables import SkuSalesTable, ProductLineTable, SelectedPLTable

@login_required
def pl_select(request):
	if 'productlines' not in request.session or request.session.get('productlines') == None:
		request.session['productlines'] = list()
	queryset = ProductLine.objects.all().exclude(id__in=request.session.get('productlines'))
	selected = ProductLine.objects.filter(id__in=request.session.get('productlines'))
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

	if request.method == 'POST':
		if 'add_all' in request.POST:
			productlines = list()
			productlines.extend(request.session.get('productlines'))
			for pl in queryset:
				productlines.append(pl.pk)
			request.session['productlines'] = productlines
			return redirect('sales_report_select')
		if 'remove_all' in request.POST:
			request.session['productlines'] = list()
			return redirect('sales_report_select')
		if 'gen_report' in request.POST:
			return redirect('sales_report')

	input_table = ProductLineTable(queryset)
	selected_table = SelectedPLTable(selected)
	context['input_table'] = input_table
	context['selected_table'] = selected_table
	context['queryset'] = queryset
	RequestConfig(request, paginate=paginate).configure(input_table)
	return render(request, 'sales/data.html', context)

@login_required
def product_line_add(request, pk):
	productlines = [pk]
	productlines.extend(request.session.get('productlines'))
	request.session['productlines'] = productlines
	return redirect('sales_report_select')

@login_required
def product_line_remove(request, pk):
	productlines = list()
	productlines.extend(request.session.get('productlines'))
	productlines.remove(pk)
	request.session['productlines'] = productlines
	return redirect('sales_report_select')

@login_required
def sales_report(request):
	context = {
		'sku_list': SKU.objects.filter(product_line__pk__in=request.session.get('productlines'))
	}
	return render(request, 'sales/report.html', context)

@login_required
def sku_drilldown(request, pk):
	context = {
		'sku': SKU.objects.get(pk=pk),
		'all_customers': Customer.objects.all(),
		'selected_customer': None,
		'start_time': (date.today() - timedelta(days=365)).isoformat(),
		'end_time': date.today().isoformat(),
	}
	queryset = SalesRecord.objects.filter(sku__pk=pk).order_by('date')
	if request.method == 'GET':
		if 'custfilter' in request.GET:
			cust_id = request.GET['custfilter']
			if cust_id != 'all':
				queryset = queryset.filter(customer__pk=cust_id)
				context['selected_customer'] = int(cust_id)
		if 'starttime' in request.GET and request.GET['starttime'] != '':
			context['start_time'] = request.GET['starttime']
		if 'endtime' in request.GET and request.GET['endtime'] != '':
			context['end_time'] = request.GET['endtime']
	queryset = queryset.filter(date__gte=context['start_time'], date__lte=context['end_time'])	
	if request.method == 'POST' and 'export_data' in request.POST:
		return CSVExport.export_to_csv('sku_sales_report', queryset)		
	table = SkuSalesTable(queryset)
	graph_records = dict()
	for record in queryset:
		week = str(record.date.isocalendar()[0]) + " wk " + str(record.date.isocalendar()[1])
		if week not in graph_records:
			graph_records[week] = 0
		graph_records[week] += record.cases_sold*record.price_per_case
	context['records'] = graph_records
	context['table'] = table
	return render(request, 'sales/sku_drilldown.html', context)