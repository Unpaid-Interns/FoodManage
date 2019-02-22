from django.shortcuts import render, redirect
from sku_manage.models import Ingredient, ProductLine, SKU, IngredientQty
from .models import ManufacturingQty, ManufacturingGoal
from .forms import GoalsForm, GoalsChoiceForm
from django.views import generic
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required

@login_required(login_url='index')
def manufacturing(request):
	if request.method == 'POST':
		form = GoalsForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			goal_obj = ManufacturingGoal(name=name, user=request.user)
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
				norm_qty = mq.caseqty.normalize()
				caseqty = '{:f}'.format(norm_qty)
				mq_info = {"name": sku.name, "sku_number": sku.sku_num, "unit_size": sku.unit_size, "units_per_case": sku.units_per_case, "case_quantity": caseqty}
				goal_list.append(mq_info)
				# Calculation and report
				mq_dict = dict()
				iqtotalslist = list()
				#iqtotalslist_pkgs = list()
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
					ingtotalunits = (i_qty * float(mq.caseqty) * formula_scale)
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

@login_required(login_url='index')
def manufqty(request):
	new_id = request.session['goal_id']
	product_lines = ProductLine.objects.all()
	goal = ManufacturingGoal.objects.get(pk=new_id)
	GoalInlineFormSet = inlineformset_factory(ManufacturingGoal, ManufacturingQty, fields=('sku', 'caseqty',), can_delete=False)
	sku_list = SKU.objects.all()
	if request.method == "POST":
		formset = GoalInlineFormSet(request.POST, request.FILES, instance=goal)
		if formset.is_valid():
			formset.save()
			return redirect('manufacturing')
	else:
		formset = GoalInlineFormSet(instance=goal)
	return render(request, 'manufacturing_goals/manufqty.html', {'formset':formset, 'sku_list': sku_list, 'product_lines': product_lines})

@login_required(login_url='index')
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

@login_required(login_url='index')
def calcresults(request):
	goal_name = request.session['goal_calc_name']
	goal_list = request.session['goal_calc_list']
	return render(request, 'manufacturing_goals/calcresults.html', {'goal_name': goal_name, 'goal_list': goal_list})

@login_required(login_url='index')
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

@login_required(login_url='index')
def manufexport(request):
	goal_name = request.session['goal_export_name']
	goal_info = request.session['goal_export_info']
	return render(request, 'manufacturing_goals/manufexport.html', {'goal_name': goal_name, 'goal_info': goal_info})

def manufdetails(request):
	goal_name = request.session['goal_name']
	goal_info = request.session['goal_export_info']
	goal_calc = request.session['goal_calc_list']
	return render(request, 'manufacturing_goals/manufdetails.html', {'goal_name': goal_name, 'goal_info': goal_info, 'goal_calc': goal_calc})
