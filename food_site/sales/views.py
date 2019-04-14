from datetime import date, timedelta, datetime
from decimal import Decimal

from manufacturing_goals import unitconvert
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django_tables2 import RequestConfig, paginators
from sku_manage.models import SKU, ProductLine, IngredientQty
from manufacturing_goals.models import ManufacturingQty
from .models import SalesRecord, Customer
from .tables import SkuSalesTable, ProductLineTable, SelectedPLTable, SkuSummaryTable, SkuTotalTable, PLSummaryTable
import urllib
import time
from exporter import CSVExport

@permission_required('sales.report_salesrecord')
def pl_select(request):
	if 'productlines' not in request.session or request.session.get('productlines') == None:
		request.session['productlines'] = list()
	queryset = ProductLine.objects.all().exclude(id__in=request.session.get('productlines'))
	selected = ProductLine.objects.filter(id__in=request.session.get('productlines'))
	context = {
		'paginated': True,
		'keyword': '',
		'all_skus': SKU.objects.all(),
		'all_customers': Customer.objects.all(),
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
			request.session['customer'] = request.POST['custfilter']
			return redirect('sales_report')

	input_table = ProductLineTable(queryset)
	selected_table = SelectedPLTable(selected)
	context['input_table'] = input_table
	context['selected_table'] = selected_table
	context['queryset'] = queryset
	RequestConfig(request, paginate=paginate).configure(input_table)
	RequestConfig(request, paginate=paginate).configure(selected_table)
	return render(request, 'sales/data.html', context)

@permission_required('sales.report_salesrecord')
def product_line_add(request, pk):
	productlines = [pk]
	productlines.extend(request.session.get('productlines'))
	request.session['productlines'] = productlines
	return redirect('sales_report_select')

@permission_required('sales.report_salesrecord')
def product_line_remove(request, pk):
	productlines = list()
	productlines.extend(request.session.get('productlines'))
	productlines.remove(pk)
	request.session['productlines'] = productlines
	return redirect('sales_report_select')

@permission_required('sales.report_salesrecord')
def sales_report(request):
	context = dict()
	tables = dict()
	totals = dict()
	all_sales = dict()
	plsummaries = dict()
	export_data = dict()
	product_lines = ProductLine.objects.filter(pk__in=request.session.get('productlines'))
	for sku in SKU.objects.filter(product_line__in=product_lines):
		sales_records = SalesRecord.objects.filter(sku=sku, date__lte=date.today(), date__gte=date.today().replace(month=1, day=1) - timedelta(days=9*365)).order_by('date')
		cust_id = request.session.get('customer')
		if cust_id != 'all':
			sales_records = sales_records.filter(customer__pk=cust_id)
		
		# Sales Calculations
		tot_revenue = 0
		tot_cases = 0
		sales_computed = list()
		sales_total = list()
		if sales_records:
			year = 0
			revenue = 0
			cases = 0
			for record in sales_records:
				tot_revenue += record.cases_sold * record.price_per_case
				tot_cases += record.cases_sold
				if year == record.date.year:
					revenue += record.cases_sold * record.price_per_case
					cases += record.cases_sold
				else:
					if year > 0:
						sales_computed.append({'year': year, 'sku': sku, 'revenue': revenue, 'revenue_per_case': round(revenue/cases, 2)})
					year = record.date.year
					revenue = record.cases_sold * record.price_per_case
					cases = record.cases_sold
			sales_computed.append({'year': year, 'sku': sku, 'revenue': revenue, 'revenue_per_case': round(revenue/cases, 2)})
			
			# Manufacturing run size
			mfg_run_size = Decimal(sku.mfg_rate * 10) # num cases in 10 hrs
			mfg_runs = ManufacturingQty.objects.filter(sku=sku, goal__enabled=True, scheduleitem__start__lte=date.today(), scheduleitem__start__gte=date.today().replace(month=1, day=1) - timedelta(days=9*365))
			if mfg_runs:
				mfg_run_tot = 0
				for run in mfg_runs:
					mfg_run_tot += run.caseqty
				mfg_run_size = Decimal(mfg_run_tot)/len(mfg_runs)

			# Total Ingredient Cost
			ingr_cost = 0
			for ingrqty in IngredientQty.objects.filter(formula=sku.formula):
				ingr_cost += Decimal(sku.formula_scale) * ingrqty.ingredient.cost * Decimal(unitconvert.convert(ingrqty.quantity, ingrqty.quantity_units, ingrqty.ingredient.package_size_units)) / Decimal(ingrqty.ingredient.package_size)

			# Totals Table
			cogs = ingr_cost + sku.mfg_setup_cost/mfg_run_size + sku.mfg_run_cost
			sales_total = [{
				'revenue': tot_revenue, 
				'mfg_run_size': mfg_run_size, 
				'ingredient_cost': round(ingr_cost, 2), 
				'mfg_setup_cost': round(sku.mfg_setup_cost/mfg_run_size, 2), 
				'mfg_run_cost': sku.mfg_run_cost, 
				'cogs': round(cogs, 2), 
				'revenue_per_case': round(tot_revenue/tot_cases, 2), 
				'profit_per_case': round(tot_revenue/tot_cases - cogs, 2), 
				'profit_margin': str(int(round(100*((tot_revenue/tot_cases) / cogs - 1), 2))) + '%',
			}]

		tables[sku] = SkuSummaryTable(sales_computed)
		RequestConfig(request, paginate=False).configure(tables[sku])
		totals[sku] = SkuTotalTable(sales_total)
		export_data[sku] = (sales_computed, sales_total)
		all_sales[sku] = sales_computed

	# Product Line Summary
	for prodline in product_lines:
		revenue_totals = dict()
		total_revenue = 0
		for sku in SKU.objects.filter(product_line=prodline):
			for sales_data in all_sales[sku]:
				year_total_revenue = sales_data['revenue']
				total_revenue += sales_data['revenue']
				if str(sales_data['year']) in revenue_totals:
					year_total_revenue += revenue_totals[str(sales_data['year'])]
				revenue_totals[str(sales_data['year'])] = year_total_revenue
		if revenue_totals:
			revenue_totals['Full Decade'] = total_revenue
		plsummary = list()
		for year, revenue in revenue_totals.items():
			plsummary.append({'year': year, 'revenue': revenue})
		plsummaries[prodline] = PLSummaryTable(plsummary)
		RequestConfig(request, paginate=False).configure(plsummaries[prodline])

	# CSV Export
	if request.method == 'POST' and 'export_data' in request.POST:
		return CSVExport.export_to_csv('sales_report', export_data)		

	context['product_lines'] = product_lines
	context['tables'] = tables
	context['totals'] = totals
	context['plsummaries'] = plsummaries
	return render(request, 'sales/report.html', context)

@permission_required('sales.report_salesrecord')
def sku_drilldown(request, pk):
	sku = SKU.objects.get(pk=pk)
	context = {
		'sku': sku,
		'all_customers': Customer.objects.all(),
		'selected_customer': None,
		'start_time': (date.today() - timedelta(days=365)).isoformat(),
		'end_time': date.today().isoformat(),
		'error': None,
	}

	# Data Acquisition
	queryset = SalesRecord.objects.filter(sku__pk=pk).order_by('-date')
	prev_customer = request.session.get('customer')
	if prev_customer != None and prev_customer != 'all':
		context['selected_customer'] = int(prev_customer)
		queryset = queryset.filter(customer__pk=prev_customer)
	request.session['customer'] = None
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

	# errors
	enddate = datetime.strptime(context['end_time'], '%Y-%m-%d').date()
	startdate = datetime.strptime(context['start_time'], '%Y-%m-%d').date()
	if enddate < startdate or enddate > date.today():
		context['error'] = 'Invalid Date Filters'
	elif startdate.year < 1999:
		context['error'] = 'No data from before 1999'
	elif enddate < startdate + timedelta(days=7):
		context['error'] = 'Data at week granularity'
	
	# CSV Export
	if request.method == 'POST' and 'export_data' in request.POST:
		return CSVExport.export_to_csv('sku_sales_report', queryset)		
	
	# Main Table
	table = SkuSalesTable(queryset)
	RequestConfig(request, paginate=False).configure(table)

	# Totals Table
	tot_revenue = 0
	tot_cases = 0
	sales_total = list()
	if queryset:
		for record in queryset:
			tot_revenue += record.cases_sold * record.price_per_case
			tot_cases += record.cases_sold
		# Manufacturing run size
		mfg_run_size = Decimal(sku.mfg_rate * 10) # num cases in 10 hrs
		mfg_runs = ManufacturingQty.objects.filter(sku=sku, goal__enabled=True, scheduleitem__start__lte=date.today(), scheduleitem__start__gte=date.today().replace(month=1, day=1) - timedelta(days=9*365))
		if mfg_runs:
			mfg_run_tot = 0
			for run in mfg_runs:
				mfg_run_tot += run.caseqty
			mfg_run_size = Decimal(mfg_run_tot)/len(mfg_runs)
		# Total Ingredient Cost
		ingr_cost = 0
		for ingrqty in IngredientQty.objects.filter(formula=sku.formula):
			ingr_cost += Decimal(sku.formula_scale) * ingrqty.ingredient.cost * Decimal(unitconvert.convert(ingrqty.quantity, ingrqty.quantity_units, ingrqty.ingredient.package_size_units)) / Decimal(ingrqty.ingredient.package_size)
		# Totals Table
		cogs = ingr_cost + sku.mfg_setup_cost/mfg_run_size + sku.mfg_run_cost
		sales_total = [{
			'revenue': tot_revenue, 
			'mfg_run_size': mfg_run_size, 
			'ingredient_cost': round(ingr_cost, 2), 
			'mfg_setup_cost': round(sku.mfg_setup_cost/mfg_run_size, 2), 
			'mfg_run_cost': sku.mfg_run_cost, 
			'cogs': round(cogs, 2), 
			'revenue_per_case': round(tot_revenue/tot_cases, 2), 
			'profit_per_case': round(tot_revenue/tot_cases - cogs, 2), 
			'profit_margin': str(int(round(100*((tot_revenue/tot_cases) / cogs - 1), 2))) + '%',
		}]

	total = SkuTotalTable(sales_total)

	# Graph
	graph_records = list()
	prev_week = None
	for record in queryset:
		week = str(record.date.isocalendar()[0]) + " wk " + str(record.date.isocalendar()[1])
		if week != prev_week:
			graph_records.append((week, 0))
		stuff = graph_records[len(graph_records) - 1]
		graph_records[len(graph_records) - 1] = (stuff[0], stuff[1] + record.cases_sold*record.price_per_case)
		prev_week = week

	graph_records.reverse()
	context['records'] = graph_records
	context['table'] = table
	context['total'] = total
	return render(request, 'sales/sku_drilldown.html', context)

@staff_member_required
def scrape(request):
	data = list()
	data.append('Sales records updated from remote server.')
	for skuo in SKU.objects.all():
		sku = skuo.sku_num
		for year in range(1999,date.today().year+1):
			time.sleep(.2)
			url = 'http://hypomeals-sales.colab.duke.edu:8080/?sku='+str(sku)+'&year='+str(year)
			dat = urllib.request.urlopen(url)
			for line in dat.readlines():
				line = str(line)
				if '<tr>' in line and '<td>' in line:
					cur = line.split('<td>')
					cust = None
					ppc = cur[7][0:(len(cur[7])-3)]
					if Customer.objects.filter(name=cur[5],number=cur[4]).exists():
						cust = Customer.objects.filter(name=cur[5],number=cur[4])[0]
					else:	
						cust = Customer.objects.create(name=cur[5],number=cur[4])
					if SalesRecord.objects.filter(
						sku = skuo,
						date = date(year=int(cur[1]), month=1, day=1)+timedelta(days=(int(cur[3])-1)*7),
						customer = cust,
						cases_sold = int(cur[6]),
						price_per_case = Decimal(ppc)
						).exists():
						continue
					srec = SalesRecord.objects.create(
						sku = skuo,
						date = date(year=int(cur[1]), month=1, day=1)+timedelta(days=(int(cur[3])-1)*7),
						customer = cust,
						cases_sold = int(cur[6]),
						price_per_case = Decimal(ppc)
						)
					data.append(srec)
	context = {
		'data': data
	}
	return render(request, 'sales/scrape_test.html', context)

