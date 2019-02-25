from django.shortcuts import render, redirect
from django.db.models import Q
from sku_manage.models import SKU, Ingredient, ProductLine, ManufacturingLine, IngredientQty, SkuMfgLine
from django_tables2 import RequestConfig, paginators
from .tables import SKUTable, MfgQtyTable
from .models import ManufacturingQty, ManufacturingGoal, ScheduleItem
from .forms import GoalsForm, GoalsChoiceForm, ManufacturingSchedForm
from django.views import generic
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
import json
from django.core.exceptions import ValidationError
from datetime import datetime

@login_required
def manufacturing(request):
	if request.method == 'POST':
		form = GoalsForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			deadline = form.cleaned_data['deadline']
			goal_obj = ManufacturingGoal(name=name, user=request.user, deadline=deadline)
			goal_obj.save()
			request.session['goal_id'] = goal_obj.id
			return redirect('manufqty')
		form2 = GoalsChoiceForm(request.POST, user=request.user)
		if form2.is_valid():
			goal = form2.cleaned_data['goal']
			goal_qty = goal.manufacturingqty_set.all()
			goal_list = list()
			goalcalc_list = list()
			for mq in goal_qty:
				# Details about the Goal itself
				sku = mq.sku
				norm_qty = mq.caseqty
				caseqty = '{:f}'.format(norm_qty)
				mq_info = {"name": sku.name, "sku_number": sku.sku_num, "unit_size": sku.unit_size, "units_per_case": sku.units_per_case, "case_quantity": caseqty}
				goal_list.append(mq_info)
				# Calculation and report
				mq_dict = dict()
				iqtotalslist = list()
				mq_dict["sku"] = str(sku)
				mq_dict["sku_num"] = sku.sku_num
				mq_dict["unit_size"] = sku.unit_size
				mq_dict["units_per_case"] = sku.units_per_case
				formula = sku.formula
				for iq in formula.ingredientqty_set.all():
					ingredient = iq.ingredient
					i_qty = iq.quantity
					formula_scale = sku.formula_scale
					ipkg_size = ingredient.package_size
					ingtotalunits = (i_qty * mq.caseqty * formula_scale)
					ingtotalpkgs = (ingtotalunits/ipkg_size)
					iqtotalslist.append({ingredient.name: ['{:g}'.format(ingtotalunits)+' '+ingredient.package_size_units, '{:g}'.format(ingtotalpkgs)+' packages']})
				mq_dict["ingredienttotals"] = iqtotalslist
				goalcalc_list.append(mq_dict)
			request.session['goal_name'] = goal.name
			request.session['goal_export_info'] = goal_list
			request.session['goal_calc_list'] = goalcalc_list
			return redirect('manufdetails')
	else:
		form = GoalsForm()
		form2 = GoalsChoiceForm(user=request.user)
	return render(request, "manufacturing_goals/manufacturing.html", {'form': form, 'form2': form2})

@login_required
def manufqty(request):
	context = {
		'paginated': True,
		'keyword': '',
		'mfg_lines': ManufacturingLine.objects.all(),
		'all_ingredients': Ingredient.objects.all(),
		'selected_ingredient': None,
		'all_product_lines': ProductLine.objects.all(),
		'selected_product_line': None,
		'errormsg': request.session.get('errormsg'),
	}	
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25,
	}
	goal = ManufacturingGoal.objects.get(pk=request.session['goal_id'])
	mfgqtys = ManufacturingQty.objects.filter(goal=goal)
	sku_list = mfgqtys.values_list('sku__id', flat=True)
	queryset = SKU.objects.exclude(id__in=sku_list)
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

		if 'done' in request.GET:
			# print(mfgqtys)
			for m in mfgqtys:
				sch_item = ScheduleItem(mfgqty=m)
				sch_item.save()
			return redirect('manufacturing')

	input_table = SKUTable(queryset)
	mfgqty_table = MfgQtyTable(mfgqtys)
	context['input_table'] = input_table
	context['selected_table'] = mfgqty_table
	RequestConfig(request, paginate=paginate).configure(input_table)
	return render(request, 'manufacturing_goals/data.html', context)

def goal_add(request, pk):
	try:
		goal = ManufacturingGoal.objects.get(pk=request.session['goal_id'])
		sku = SKU.objects.get(pk=pk)
		caseqty = request.POST['case_qty']
		ManufacturingQty(sku=sku, goal=goal, caseqty=caseqty).save()
		request.session['errormsg'] = ''
	except ValidationError:
		request.session['errormsg'] = 'Include Case Quantity'
	return redirect('manufqty')

def goal_remove(request, pk):
	ManufacturingQty.objects.get(pk=pk).delete()
	request.session['errormsg'] = ''
	return redirect('manufqty')

@login_required
def manufcalc(request):
	form = GoalsChoiceForm(user=request.user)
	if request.method == "POST":
		form = GoalsChoiceForm(request.POST, user=request.user)
		if form.is_valid():
			goalcalc_list = list()
			goal = form.cleaned_data['goal']
			goal_qty = goal.manufacturingqty_set.all()
			for mq in goal_qty:
				mq_dict = dict()
				iq_totalslist = list()
				sku = mq.sku
				mq_dict["sku"] = str(sku)
				mq_dict["sku_num"] = sku.sku_num
				mq_dict["unit_size"] = sku.unit_size
				mq_dict["units_per_case"] = sku.units_per_case
				ingredientqtys = sku.ingredientqty_set.all()
				for iq in ingredientqtys:
					ingredient = iq.ingredient
					i_qty = iq.quantity
					ingtotal = (i_qty * mq.caseqty).normalize()
					iq_totalslist.append({ingredient.name: '{:f}'.format(ingtotal)})
				mq_dict["ingredienttotals"] = iq_totalslist
				goalcalc_list.append(mq_dict)
			request.session['goal_calc_name'] = goal.name
			request.session['goal_calc_list'] = goalcalc_list
			return redirect('calcresults')
	return render(request, 'manufacturing_goals/manufcalc.html', {'form': form})

@login_required
def calcresults(request):
	goal_name = request.session['goal_calc_name']
	goal_list = request.session['goal_calc_list']
	return render(request, 'manufacturing_goals/calcresults.html', {'goal_name': goal_name, 'goal_list': goal_list})

@login_required
def manufcsv(request):
	form = GoalsChoiceForm(user=request.user)
	if request.method == "POST":
		form = GoalsChoiceForm(request.POST, user=request.user)
		if form.is_valid():
			goal = form.cleaned_data['goal']
			goal_qty = goal.manufacturingqty_set.all()
			goal_list = list()
			for mq in goal_qty:
				sku = mq.sku
				norm_qty = mq.caseqty.normalize()
				caseqty = '{:f}'.format(norm_qty)
				mq_info = {"name": sku.name, "sku_number": sku.sku_num, "unit_size": sku.unit_size, "units_per_case": sku.units_per_case, "case_quantity": caseqty}
				goal_list.append(mq_info)
			request.session['goal_export_name'] = goal.name
			request.session['goal_export_info'] = goal_list
			return redirect('manufexport')
	return render(request, 'manufacturing_goals/manufcsv.html', {'form': form})

@login_required
def manufexport(request):
	goal_name = request.session['goal_export_name']
	goal_info = request.session['goal_export_info']
	return render(request, 'manufacturing_goals/manufexport.html', {'goal_name': goal_name, 'goal_info': goal_info})

@login_required
def manufdetails(request):
	goal_name = request.session['goal_name']
	goal_info = request.session['goal_export_info']
	goal_calc = request.session['goal_calc_list']
	return render(request, 'manufacturing_goals/manufdetails.html', {'goal_name': goal_name, 'goal_info': goal_info, 'goal_calc': goal_calc})

@login_required(login_url='index')
def timeline(request):
	# add in code to send db stored timeline as JSON and recieve timeline as JSON and place in db
	form = ManufacturingSchedForm()
	scheditems = ScheduleItem.objects.all()
	tldata_list = list()
	data_list = list()
	mfgl_list = list()
	mfdurations = list()
	if not scheditems:
		pass
	else:
		for s in scheditems:
			# populate js with data from existing schedule items
			data_item = dict()
			data_item['content'] = '' + s.mfgqty.goal.name + ': ' + s.mfgqty.sku.name + ', due by ' + '{:%Y-%m-%d}'.format(s.mfgqty.goal.deadline)
			data_item['id'] = s.pk
			if s.mfgline:
				data_item['group'] = s.mfgline.pk
			data_item['type'] = 'range'
			if s.start:
				data_item['start'] = s.start.strftime("%Y-%m-%dT%H:%M:%S%z")
				if s.endoverride:
					data_item['end'] = s.endoverride.strftime("%Y-%m-%dT%H:%M:%S%z")
				else:
					data_item['end'] = s.end().strftime("%Y-%m-%dT%H:%M:%S%z")
				tldata_list.append(data_item)
			else:
				data_list.append(data_item)
			duration = dict()
			duration['id'] = s.pk
			# raw, how many hours it takes via calculated time
			ttl_hrs = s.duration().seconds / 3600.0
			# 8 hours per day of work can be done, so the number of times 8 goes into a duration is how many work days it takes
			ttl_wrkd = ttl_hrs // 8
			hrs = (ttl_wrkd * 24) # gives the appearance of multiple days on the timeline
			# and the remainder is the additional hours needed to add on
			hrs = hrs + (ttl_hrs % 8)
			duration['duration'] = hrs
			mfdurations.append(duration)
		for mfgl in ManufacturingLine.objects.all():
			mfg_lines = dict()
			mfg_lines['content'] = '' + mfgl.name + ' (' + mfgl.shortname + ')'
			mfg_lines['id'] = mfgl.pk
			mfgl_list.append(mfg_lines)
	#print("Data List (not in timeline)")	
	#print(data_list)
	#print("TL Data List (in timeline)")
	#print(tldata_list)
	#print("Manuf. Lines (groups in timeline)")
	#print(mfgl_list)
	
	if request.method == "POST":
		form = ManufacturingSchedForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data['data']
			overrides = form.cleaned_data['overrides']
			d = json.loads(data)
			#print(d)
			ovr = json.loads(overrides)
			#print(ovr)
			ids_in_tl = list()
			for item in d:
				# actually store the information
				#print(item)
				schedItem = ScheduleItem.objects.get(pk=item['id'])
				schedItem.mfgline = ManufacturingLine.objects.get(pk=item['group'])
				if len(item['start'].split('.'))>1:
					schedItem.start = datetime.strptime(item['start'].split('.')[0]+'+0000', '%Y-%m-%dT%H:%M:%S%z')
				elif len(item['start'].split(':'))>=4:
					schedItem.start = datetime.strptime(item['start'].split(':')[0]+':'+item['start'].split(':')[1]+':'+item['start'].split(':')[2]+item['start'].split(':')[3], '%Y-%m-%dT%H:%M:%S%z')
				else:
					schedItem.start = datetime.strptime(item['start'], '%Y-%m-%dT%H:%M:%S%z')
				ids_in_tl.append(item['id'])
				schedItem.save()
			for i in tldata_list:
				# if it WAS in the TL, and now its not, remove info
				if i['id'] in ids_in_tl:
					pass
				else:
					schedItem2 = ScheduleItem.objects.get(pk=i['id'])
					schedItem2.mfgline = None
					schedItem2.start = None
					schedItem2.save()
			for ovr_item in ovr:
				# if the duration was manually overridden, reflect that here
				#print(
				schedItem3 = ScheduleItem.objects.get(pk=ovr_item)
				for item in d:
					if item['id'] == ovr_item:
						if len(item['end'].split('.'))>1:
							schedItem3.endoverride = datetime.strptime(item['end'].split('.')[0]+'+0000', '%Y-%m-%dT%H:%M:%S%z')
						elif len(item['end'].split(':'))>=4:
							schedItem3.endoverride = datetime.strptime(item['end'].split(':')[0]+':'+item['end'].split(':')[1]+':'+item['end'].split(':')[2]+item['end'].split(':')[3], '%Y-%m-%dT%H:%M:%S%z')
						else:
							schedItem3.endoverride = datetime.strptime(item['end'], '%Y-%m-%dT%H:%M:%S%z')
				#print(schedItem3.endoverride)
						schedItem3.save()
			return redirect('manufacturing')
	return render(request, 'manufacturing_goals/manufscheduler.html', {'form': form, 'data_list': data_list, 'tldata_list': tldata_list, 'mfgl_list': mfgl_list, 'mfdurations': mfdurations})
