from django.shortcuts import render, redirect
from sku_manage.models import Ingredient, ProductLine, SKU, IngredientQty, ManufacturingQty, ManufacturingGoal
from .forms import GoalsForm, GoalChoiceForm
from django.views import generic
from django.forms import inlineformset_factory

def manufacturing(request):
	if request.method == 'POST':
		form = GoalsForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			goal_obj = ManufacturingGoal(name=name, user=request.user)
			goal_obj.save()
			request.session['goal_id'] = goal_obj.id
			return redirect('manufqty')
	else:
		form = GoalsForm()
	return render(request, "manufacturing_goals/manufacturing.html", {'form': form})

def manufqty(request):
	new_id = request.session['goal_id']
	goal = ManufacturingGoal.objects.get(pk=new_id)
	GoalInlineFormSet = inlineformset_factory(ManufacturingGoal, ManufacturingQty, fields=('sku', 'caseqty',))
	sku_list = SKU.objects.all()
	if request.method == "POST":
		formset = GoalInlineFormSet(request.POST, request.FILES, instance=goal)
		if formset.is_valid():
			formset.save()
			return redirect('manufacturing')
	else:
		formset = GoalInlineFormSet(instance=goal)
	return render(request, 'manufacturing_goals/manufqty.html', {'formset':formset, 'sku_list': sku_list})

def manufcalc(request):
	form = GoalChoiceForm()
	if request.method == "POST":
		form = GoalChoiceForm(request.POST)
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
					iq_totalslist.append({ingredient.name: str(ingtotal)})
				mq_dict["ingredienttotals"] = iq_totalslist
				goalcalc_list.append(mq_dict)
			request.session['goal_calc_name'] = goal.name
			request.session['goal_calc_list'] = goalcalc_list
			return redirect('calcresults')
	return render(request, 'manufacturing_goals/manufcalc.html', {'form': form})

def calcresults(request):
	goal_name = request.session['goal_calc_name']
	goal_list = request.session['goal_calc_list']
	return render(request, 'manufacturing_goals/calcresults.html', {'goal_name': goal_name, 'goal_list': goal_list})

def manufcsv(request):
	form = GoalChoiceForm(user=request.user)
	if request.method == "POST":
		form = GoalChoiceForm(request.POST, user=request.user)
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

def manufexport(request):
	goal_name = request.session['goal_export_name']
	goal_info = request.session['goal_export_info']
return render(request, 'manufacturing_goals/manufexport.html', {'goal_name': goal_name, 'goal_info': goal_info})
