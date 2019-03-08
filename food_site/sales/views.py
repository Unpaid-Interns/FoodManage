from datetime import date, timedelta

from django.shortcuts import render
from sku_manage.models import SKU
from .models import SalesRecord, Customer
from .tables import SkuSalesTable

def sku_drilldown(request, pk):
	context = {
		'sku': SKU.objects.get(pk=pk),
		'all_customers': Customer.objects.all(),
		'selected_customer': None,
		'start_time': (date.today() - timedelta(days=365)).isoformat(),
		'end_time': date.today().isoformat(),
	}
	queryset = SalesRecord.objects.filter(sku__pk=pk)
	if request.method == 'GET':
		if 'custfilter' in request.GET:
			cust_id = request.GET['custfilter']
			if cust_id != 'all':
				queryset = queryset.filter(customer__pk=cust_id)
				context['selected_customer'] = int(cust_id)
		if 'starttime' in request.GET and request.GET['starttime'] != '':
			start_time = request.GET['starttime']
			context['start_time'] = start_time
			queryset = queryset.filter(date__gte=start_time)
		if 'endtime' in request.GET and request.GET['endtime'] != '':
			end_time = request.GET['endtime']
			context['end_time'] = end_time
			queryset = queryset.filter(date__lte=end_time)			
	table = SkuSalesTable(queryset)
	context['table'] = table
	return render(request, 'sales/sku_drilldown.html', context)