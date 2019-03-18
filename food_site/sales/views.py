from datetime import date, timedelta
from decimal import Decimal

from manufacturing_goals import unitconvert
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django_tables2 import RequestConfig, paginators
from sku_manage.models import SKU, ProductLine, IngredientQty
from manufacturing_goals.models import ManufacturingQty
from .models import SalesRecord, Customer
from .tables import SkuSalesTable, ProductLineTable, SelectedPLTable, SkuSummaryTable, SkuTotalTable

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
	context = dict()
	tables = dict()
	totals = dict()
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
						sales_computed.append({'year': year, 'sku': sku, 'revenue': revenue, 'revenue_per_case': (revenue/cases)})
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
			cogs = ingr_cost + (sku.mfg_setup_cost + sku.mfg_run_cost) / mfg_run_size
			sales_total = [{
				'revenue': tot_revenue, 
				'mfg_run_size': mfg_run_size, 
				'ingredient_cost': round(ingr_cost, 2), 
				'mfg_setup_cost': round(sku.mfg_setup_cost/mfg_run_size, 2), 
				'mfg_run_cost': round(sku.mfg_run_cost/mfg_run_size, 2), 
				'cogs': round(cogs, 2), 
				'revenue_per_case': round(tot_revenue/tot_cases, 2), 
				'profit_per_case': round(tot_revenue/tot_cases - cogs, 2), 
				'profit_margin': str(int(round(100*((tot_revenue/tot_cases) / cogs - 1), 2))) + '%',
			}]

		tables[sku] = SkuSummaryTable(sales_computed)
		totals[sku] = SkuTotalTable(sales_total)
		export_data[sku] = (sales_computed, sales_total)

	# CSV Export
	if request.method == 'POST' and 'export_data' in request.POST:
		return CSVExport.export_to_csv('sales_report', export_data)		

	context['product_lines'] = product_lines
	context['tables'] = tables
	context['totals'] = totals
	return render(request, 'sales/report.html', context)

@login_required
def sku_drilldown(request, pk):
	sku = SKU.objects.get(pk=pk)
	context = {
		'sku': sku,
		'all_customers': Customer.objects.all(),
		'selected_customer': None,
		'start_time': (date.today() - timedelta(days=365)).isoformat(),
		'end_time': date.today().isoformat(),
	}

	# Data Acquisition
	queryset = SalesRecord.objects.filter(sku__pk=pk).order_by('date')
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
	
	# CSV Export
	if request.method == 'POST' and 'export_data' in request.POST:
		return CSVExport.export_to_csv('sku_sales_report', queryset)		
	
	# Main Table
	table = SkuSalesTable(queryset)

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
		cogs = ingr_cost + (sku.mfg_setup_cost + sku.mfg_run_cost) / mfg_run_size
		sales_total = [{
			'revenue': tot_revenue, 
			'mfg_run_size': mfg_run_size, 
			'ingredient_cost': round(ingr_cost, 2), 
			'mfg_setup_cost': round(sku.mfg_setup_cost/mfg_run_size, 2), 
			'mfg_run_cost': round(sku.mfg_run_cost/mfg_run_size, 2), 
			'cogs': round(cogs, 2), 
			'revenue_per_case': round(tot_revenue/tot_cases, 2), 
			'profit_per_case': round(tot_revenue/tot_cases - cogs, 2), 
			'profit_margin': str(int(round(100*((tot_revenue/tot_cases) / cogs - 1), 2))) + '%',
		}]

	total = SkuTotalTable(sales_total)

	# Graph
	graph_records = dict()
	for record in queryset:
		week = str(record.date.isocalendar()[0]) + " wk " + str(record.date.isocalendar()[1])
		if week not in graph_records:
			graph_records[week] = 0
		graph_records[week] += record.cases_sold*record.price_per_case

	context['records'] = graph_records
	context['table'] = table
	context['total'] = total
	return render(request, 'sales/sku_drilldown.html', context)