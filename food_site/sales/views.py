from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from sku_manage.models import SKU
from .models import SalesRecord, Customer
from .tables import SkuSalesTable

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