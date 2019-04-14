from django.shortcuts import render, redirect
from django.db.models import Q
from sku_manage.models import SKU, Ingredient, ProductLine, ManufacturingLine, IngredientQty, SkuMfgLine
from django_tables2 import RequestConfig, paginators
from .tables import SKUTable, MfgQtyTable, EnableTable, SKUTable2, AutoAddTable, AutoRemoveTable
from .models import ManufacturingQty, ManufacturingGoal, ScheduleItem
from home.models import PlantManager
from .forms import GoalsForm, ManufacturingSchedForm
from django.views import generic
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
import json
from django.core.exceptions import ValidationError
from datetime import datetime, date, time, timedelta
from manufacturing_goals.autoschedule import autoschedule
from . import unitconvert
from sales.models import SalesRecord
from django.utils import timezone
import math

@permission_required('manufacturing_goals.view_manufacturinggoal')
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
        if 'goal' in request.POST:
            goal = ManufacturingGoal.objects.get(pk=request.POST['goal'])
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
                    ingtotalunits = (unitconvert.convert(iq.quantity, iq.quantity_units, iq.ingredient.package_size_units) * mq.caseqty * sku.formula_scale)
                    ingtotalpkgs = (ingtotalunits/iq.ingredient.package_size)
                    iqtotalslist.append({iq.ingredient.name: ['{:g}'.format(ingtotalunits)+' '+iq.ingredient.package_size_units, '{:g}'.format(ingtotalpkgs)+' packages']})
                mq_dict["ingredienttotals"] = iqtotalslist
                goalcalc_list.append(mq_dict)
            request.session['goal_name'] = goal.name
            request.session['goal_export_info'] = goal_list
            request.session['goal_calc_list'] = goalcalc_list
            request.session['goal_id'] = goal.id
            return redirect('manufdetails')

    form = GoalsForm()
    queryset = ManufacturingGoal.objects.all()
    table = EnableTable(queryset)
    RequestConfig(request, paginate=False).configure(table)
    context = {
        'enable_table': table,
        'form': form,
    }
    return render(request, "manufacturing_goals/manufacturing.html", context)

@permission_required('manufacturing_goals.add_manufacturinggoal')
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
        'startday': '',
        'startmonth': '',
        'endday': '',
        'endmonth': '',
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
                Q(mfg_rate__iexact=keyword) |
                Q(mfg_setup_cost__iexact=keyword) |
                Q(mfg_run_cost__iexact=keyword) |
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

    if request.method == 'POST':
        if 'done' in request.POST:
            return redirect('manufacturing')
        if 'delete' in request.POST:
            goal.delete()
            return redirect('manufacturing')

    input_table = SKUTable(queryset)
    mfgqty_table = MfgQtyTable(mfgqtys)
    context['input_table'] = input_table
    context['selected_table'] = mfgqty_table
    sday = request.session.get('start_day', '')
    smonth = request.session.get('start_month', '')
    eday = request.session.get('end_day', '')
    emonth = request.session.get('end_month', '')
    context['startday'] = sday
    context['startmonth'] = smonth
    context['endday'] = eday
    context['endmonth'] = emonth
    RequestConfig(request, paginate=paginate).configure(input_table)
    RequestConfig(request, paginate=paginate).configure(mfgqty_table)
    return render(request, 'manufacturing_goals/data.html', context)

@permission_required('manufacturing_goals.add_manufacturinggoal')
def goal_add(request, pk):
    try:
        goal = ManufacturingGoal.objects.get(pk=request.session['goal_id'])
        sku = SKU.objects.get(pk=pk)
        caseqty = request.POST['case_qty']
        ManufacturingQty(sku=sku, goal=goal, caseqty=caseqty).save()
        goal.save()
        request.session['errormsg'] = ''
    except (ValueError, ValidationError):
        request.session['errormsg'] = 'Include Case Quantity'
    return redirect('manufqty')

@permission_required('manufacturing_goals.add_manufacturinggoal')
def goal_remove(request, pk):
    goal = ManufacturingGoal.objects.get(pk=request.session['goal_id'])
    ManufacturingQty.objects.get(pk=pk).delete()
    goal.save()
    request.session['errormsg'] = ''
    return redirect('manufqty')

@permission_required('manufacturing_goals.view_manufacturinggoal')
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

@permission_required('manufacturing_goals.view_manufacturinggoal')
def calcresults(request):
    goal_name = request.session['goal_calc_name']
    goal_list = request.session['goal_calc_list']
    return render(request, 'manufacturing_goals/calcresults.html', {'goal_name': goal_name, 'goal_list': goal_list})

@permission_required('manufacturing_goals.view_manufacturinggoal')
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

@permission_required('manufacturing_goals.view_manufacturinggoal')
def manufexport(request):
    goal_name = request.session['goal_export_name']
    goal_info = request.session['goal_export_info']
    return render(request, 'manufacturing_goals/manufexport.html', {'goal_name': goal_name, 'goal_info': goal_info})

@permission_required('manufacturing_goals.view_manufacturinggoal')
def manufdetails(request):
    goal_name = request.session['goal_name']
    goal_info = request.session['goal_export_info']
    goal_calc = request.session['goal_calc_list']
    sched_dep = len(ScheduleItem.objects.filter(mfgqty__goal__pk=request.session['goal_id']))
    goal = ManufacturingGoal.objects.get(pk=request.session['goal_id'])
    return render(request, 'manufacturing_goals/manufdetails.html', {'goal_name': goal_name, 'goal_info': goal_info, 'goal_calc': goal_calc, 'schedule_dep': sched_dep, 'goal': goal})

@permission_required('manufacturing_goals.change_scheduleitem')
def timeline(request):
    request.session['mfgqtys'] = list()
    context = dict()
    mfg_qtys = ManufacturingQty.objects.filter(goal__enabled=True)
    accessible_lines = list()
    accessible_lines = ManufacturingLine.objects.filter(plantmanager__user=request.user)
    if request.user.is_superuser:
        accessible_lines = ManufacturingLine.objects.all()
        #accessible_lines = list() #for testing purposes only
    print(accessible_lines)
    for mfg_qty in mfg_qtys:
        sched_items = ScheduleItem.objects.filter(mfgqty=mfg_qty)
        mfg_lines = ManufacturingLine.objects.filter(skumfgline__sku__manufacturingqty=mfg_qty)
        #print("Length of list of mfg_lines: " + len(mfg_lines))
        #print("Length of list of sched_items: " + len(sched_items))
        #print("First mfg_line: " + mfg_lines[0])
        if len(mfg_lines) > 0 and len(sched_items) == 0 and mfg_lines[0]:
            ScheduleItem(mfgqty=mfg_qty, mfgline=mfg_lines[0]).save()
    # add in code to send db stored timeline as JSON and recieve timeline as JSON and place in db
    form = ManufacturingSchedForm()
    scheditems = ScheduleItem.objects.all()
    mfdurations = list()
    mfg_overlap = list()
    if not scheditems:
        pass
    else:
        for s in scheditems:
            duration = dict()
            duration['id'] = s.pk
            # raw, how many hours it takes via calculated time
            ttl_hrs = s.duration().seconds / 3600.0
            # 10 hours per day of work can be done, so the number of times 8 goes into a duration is how many work days it takes
            ttl_wrkd = ttl_hrs // 10
            hrs = (ttl_wrkd * 24) # gives the appearance of multiple days on the timeline
            # and the remainder is the additional hours needed to add on
            hrs = hrs + (ttl_hrs % 10)
            duration['duration'] = hrs
            duration['mfline'] = s.mfgline.pk
            mfdurations.append(duration)
            for s2 in scheditems:
                if s.start is not None and s2.start is not None and s != s2 and s.mfgline == s2.mfgline and s.mfgqty.sku.sku_num < s2.mfgqty.sku.sku_num and not (s.start >= s2.end() or s.end() <= s2.start):
                    mfg_overlap.append(str(s.mfgline) + ': ' + str(s.mfgqty.goal) + ': ' + str(s.mfgqty.sku) + ' ----- ' + str(s2.mfgqty.goal) + ': ' + str(s2.mfgqty.sku))

    
    if request.method == "POST":
        form = ManufacturingSchedForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']
            overrides = form.cleaned_data['overrides']
            json_data = json.loads(data)
            ovr = json.loads(overrides)
            print("Data:\n")
            print(data)
            print("Overrides:\n")
            print(ovr)
            ids_in_tl = list()
            for item in json_data:
                # actually store the information
                schedItem = ScheduleItem.objects.get(pk=item['id'])
                schedItem.mfgline = ManufacturingLine.objects.get(pk=item['group'])
                if len(item['start'].split('.'))>1:
                    datatime = datetime.strptime(item['start'].split('.')[0]+'+0000', '%Y-%m-%dT%H:%M:%S%z')
                    if datatime.time() < time(8,0,0):
                        datatime.replace(datatime.year, datatime.month, datatime.day, 8, 0, 0, 0, datatime.tzinfo)
                    elif datatime.time() > time(18,0,0):
                        datatime.replace(datatime.year, datatime.month, datatime.day, 18, 0, 0, 0, datatime.tzinfo)
                    print(datatime)
                    schedItem.start = datatime
                elif len(item['start'].split(':'))>=4:
                    datatime = datetime.strptime(item['start'].split(':')[0]+':'+item['start'].split(':')[1]+':'+item['start'].split(':')[2]+item['start'].split(':')[3], '%Y-%m-%dT%H:%M:%S%z')
                    if datatime.time() < time(8,0,0):
                        datatime.replace(datatime.year, datatime.month, datatime.day, 8, 0, 0, 0, datatime.tzinfo)
                    elif datatime.time() > time(18,0,0):
                        datatime.replace(datatime.year, datatime.month, datatime.day, 18, 0, 0, 0, datatime.tzinfo)
                    print(datatime)
                    schedItem.start = datatime
                else:
                    datatime = datetime.strptime(item['start'], '%Y-%m-%dT%H:%M:%S%z')
                    if datatime.time() < time(8,0,0):
                        datatime.replace(datatime.year, datatime.month, datatime.day, 8, 0, 0, 0, datatime.tzinfo)
                    elif datatime.time() > time(18,0,0):
                        datatime.replace(datatime.year, datatime.month, datatime.day, 18, 0, 0, 0, datatime.tzinfo)
                    print(datatime)
                    schedItem.start = datatime
                ids_in_tl.append(item['id'])
                schedItem.save()
            print(ids_in_tl)
            print(ScheduleItem.objects.all().values('pk'))
            for pk in ScheduleItem.objects.all().values('pk'):
                # if it WAS in the TL, and now its not, remove info
                # as of yet, doesn't delete anything
                # I believe that it recreates the ScheduleItem b/c of the POST
                print(pk['pk'])
                if pk['pk'] not in ids_in_tl:
                    removed_item = ScheduleItem.objects.get(pk=pk['pk'])
                    removed_item.start = None
                    removed_item.delete()
            for ovr_item in ovr:
                # if the duration was manually overridden, reflect that here
                #print(
                end_override_item = ScheduleItem.objects.get(pk=ovr_item)
                for item in json_data:
                    if item['id'] == ovr_item:
                        if len(item['end'].split('.'))>1:
                            end_override_item.endoverride = datetime.strptime(item['end'].split('.')[0]+'+0000', '%Y-%m-%dT%H:%M:%S%z')
                        elif len(item['end'].split(':'))>=4:
                            end_override_item.endoverride = datetime.strptime(item['end'].split(':')[0]+':'+item['end'].split(':')[1]+':'+item['end'].split(':')[2]+item['end'].split(':')[3], '%Y-%m-%dT%H:%M:%S%z')
                        else:
                            end_override_item.endoverride = datetime.strptime(item['end'], '%Y-%m-%dT%H:%M:%S%z')
                        end_override_item.save()

            return redirect('timeline')
    context['form'] = form, 
    context['unscheduled_items'] = ScheduleItem.objects.filter(start__isnull=True)
    context['scheduled_items'] = ScheduleItem.objects.filter(start__isnull=False)
    visible_unsch_item = list()
    visible_sch_item = list()
    for ui in context['unscheduled_items']:
        if ui.mfgline in accessible_lines:
            visible_unsch_item.append(ui)
    for si in context['scheduled_items']:
        if si.mfgline in accessible_lines:
            visible_sch_item.append(si)
        print("Start Time:\n")      
        print(si.start)
    context['visible_scheduled_items'] = visible_sch_item
    context['visible_unscheduled_items'] = visible_unsch_item
    #context['mfg_lines'] = ManufacturingLine.objects.all()
    context['mfg_lines'] = accessible_lines
    context['mfdurations'] = mfdurations
    context['mfg_overlap'] = mfg_overlap
    #context['provisional_items'] = ScheduleItem.objects.filter(provisional_user__isnull=False) needs a stricter criteria?
    print(mfg_overlap)
    return render(request, 'manufacturing_goals/manufscheduler.html', context)

@permission_required('manufacturing_goals.view_manufacturinggoal')
def timeline_viewer(request):
    context = dict()
    mfg_qtys = ManufacturingQty.objects.filter(goal__enabled=True)
    accessible_lines = list()
    accessible_lines = ManufacturingLine.objects.filter(plantmanager__user=request.user)
    if request.user.is_superuser:
        accessible_lines = ManufacturingLine.objects.all()
        #accessible_lines = list() #for testing purposes only
    print(accessible_lines)
    for mfg_qty in mfg_qtys:
        sched_items = ScheduleItem.objects.filter(mfgqty=mfg_qty)
        mfg_lines = ManufacturingLine.objects.filter(skumfgline__sku__manufacturingqty=mfg_qty)
        if len(mfg_lines) > 0 and len(sched_items) == 0 and mfg_lines[0]:
            ScheduleItem(mfgqty=mfg_qty, mfgline=mfg_lines[0]).save()
    # add in code to send db stored timeline as JSON and recieve timeline as JSON and place in db
    form = ManufacturingSchedForm()
    scheditems = ScheduleItem.objects.all()
    mfdurations = list()
    mfg_overlap = list()
    if not scheditems:
        pass
    else:
        for s in scheditems:
            duration = dict()
            duration['id'] = s.pk
            # raw, how many hours it takes via calculated time
            ttl_hrs = s.duration().seconds / 3600.0
            # 10 hours per day of work can be done, so the number of times 8 goes into a duration is how many work days it takes
            ttl_wrkd = ttl_hrs // 10
            hrs = (ttl_wrkd * 24) # gives the appearance of multiple days on the timeline
            # and the remainder is the additional hours needed to add on
            hrs = hrs + (ttl_hrs % 10)
            duration['duration'] = hrs
            duration['mfline'] = s.mfgline.pk
            mfdurations.append(duration)
            for s2 in scheditems:
                if s.start is not None and s2.start is not None and s != s2 and s.mfgline == s2.mfgline and s.mfgqty.sku.sku_num < s2.mfgqty.sku.sku_num and not (s.start >= s2.end() or s.end() <= s2.start):
                    mfg_overlap.append(str(s.mfgline) + ': ' + str(s.mfgqty.goal) + ': ' + str(s.mfgqty.sku) + ' ----- ' + str(s2.mfgqty.goal) + ': ' + str(s2.mfgqty.sku))
    context['form'] = form, 
    context['unscheduled_items'] = ScheduleItem.objects.filter(start__isnull=True)
    context['scheduled_items'] = ScheduleItem.objects.filter(start__isnull=False)
    visible_unsch_item = list()
    visible_sch_item = list()
    for ui in context['unscheduled_items']:
        if ui.mfgline in accessible_lines:
            visible_unsch_item.append(ui)
    for si in context['scheduled_items']:
        if si.mfgline in accessible_lines:
            visible_sch_item.append(si)
        print("Start Time:\n")      
        print(si.start)
    context['visible_scheduled_items'] = visible_sch_item
    context['visible_unscheduled_items'] = visible_unsch_item
    context['mfg_lines'] = ManufacturingLine.objects.all()
    #context['mfg_lines'] = accessible_lines
    context['mfdurations'] = mfdurations
    context['mfg_overlap'] = mfg_overlap
    print(mfg_overlap)
    return render(request, 'manufacturing_goals/manufsched_view.html', context)

@permission_required('manufacturing_goals.enable_manufacturinggoal')
def enable_menu(request):
    context = dict()    
    queryset = ManufacturingGoal.objects.all()
    table = EnableTable(queryset)
    context['table'] = table
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'manufacturing_goals/enable_menu.html', context)

@permission_required('manufacturing_goals.enable_manufacturinggoal')
def enable_goal(request, pk):
    goal = ManufacturingGoal.objects.get(pk=pk)
    context = {'goal' : goal}
    if request.method == 'POST':
        if 'yes' in request.POST:
            goal.enabled = not goal.enabled;
            goal.full_clean()
            goal.save()
            return redirect('manufacturing')
        if 'no' in request.POST:
            return redirect('manufacturing')
    return render(request, 'manufacturing_goals/enable_goal.html', context)

@permission_required('manufacturing_goals.change_scheduleitem')
def auto_schedule_select(request):
    if 'mfgqtys' not in request.session or request.session.get('mfgqtys') == None:
        request.session['mfgqtys'] = list()
    queryset = ManufacturingQty.objects.filter(scheduleitem__start__isnull=True, goal__enabled=True)
    selected_set = queryset.filter(id__in=request.session.get('mfgqtys'))
    queryset = queryset.exclude(id__in=request.session.get('mfgqtys'))
    input_table = AutoAddTable(queryset)
    selected_table = AutoRemoveTable(selected_set)
    context = {
        'input_table': input_table,
        'selected_table': selected_table,
        'start_date': (date.today() + timedelta(days=1)).isoformat(),
        'start_time': time(hour=8).isoformat()[0:-3],
        'end_date': (date.today() + timedelta(days=61)).isoformat(),
        'end_time': time(hour=18).isoformat()[0:-3],
    }

    if request.method == 'GET':
        if 'startdate' in request.GET and request.GET['startdate'] != '':
            request.session['auto_start_date'] = request.GET['startdate']
        if 'starttime' in request.GET and request.GET['starttime'] != '':
            request.session['auto_start_time'] = request.GET['starttime']
        if 'enddate' in request.GET and request.GET['enddate'] != '':
            request.session['auto_end_date'] = request.GET['enddate']
        if 'endtime' in request.GET and request.GET['endtime'] != '':
            request.session['auto_end_time'] = request.GET['endtime']

    if 'auto_start_date' in request.session and request.session['auto_start_date'] != '':
        context['start_date'] = request.session['auto_start_date']
    if 'auto_start_time' in request.session and request.session['auto_start_time'] != '':
        context['start_time'] = request.session['auto_start_time']
    if 'auto_end_date' in request.session and request.session['auto_end_date'] != '':
        context['end_date'] = request.session['auto_end_date']
    if 'auto_end_time' in request.session and request.session['auto_end_time'] != '':
        context['end_time'] = request.session['auto_end_time']

    request.session['auto_start_date'] = context['start_date']
    request.session['auto_start_time'] = context['start_time']
    request.session['auto_end_date'] = context['end_date']
    request.session['auto_end_time'] = context['end_time']

    RequestConfig(request, paginate=None).configure(input_table)
    RequestConfig(request, paginate=None).configure(selected_table)
    return render(request, 'manufacturing_goals/autoscheduleselect.html', context)

@permission_required('manufacturing_goals.change_scheduleitem')
def auto_schedule_add(request, pk):
    mfgqtys = [pk]
    mfgqtys.extend(request.session.get('mfgqtys'))
    request.session['mfgqtys'] = mfgqtys
    return redirect('auto_schedule_select')

@permission_required('manufacturing_goals.change_scheduleitem')
def auto_schedule_remove(request, pk):
    mfgqtys = list()
    mfgqtys.extend(request.session.get('mfgqtys'))
    mfgqtys.remove(pk)
    request.session['mfgqtys'] = mfgqtys
    return redirect('auto_schedule_select')

@permission_required('manufacturing_goals.change_scheduleitem')
def auto_schedule(request):
    debug = False
    if debug:
        start_time = datetime.today()
        stop_time = start_time + (timedelta(days=3))
        manufacturingQtys_to_be_scheduled = ManufacturingQty.objects.filter(goal__enabled=True)
    else:
        start_time = datetime.strptime(request.session.get('auto_start_date') + ' ' + request.session.get('auto_start_time'), '%Y-%m-%d %H:%M')
        stop_time = datetime.strptime(request.session.get('auto_end_date') + ' ' + request.session.get('auto_end_time'), '%Y-%m-%d %H:%M')
        manufacturingQtys_to_be_scheduled = ManufacturingQty.objects.filter(id__in=request.session.get('mfgqtys'))
    current_user = request.user
    success, message, scheduled_items, unscheduled_items = \
        autoschedule(start_time, stop_time, manufacturingQtys_to_be_scheduled, current_user)
    print(message)
    return redirect("timeline")

@permission_required('manufacturing_goals.change_manufacturinggoal')
def project(request, pk):
    sku = SKU.objects.get(pk=pk)    
    yearstart = date(2000,1,1)
    yearend = date(2000,12,31)
    sday = request.session.get('start_day', '')
    smonth = request.session.get('start_month', '')
    eday = request.session.get('end_day', '')
    emonth = request.session.get('end_month', '')
    numbersold1 = 0;
    numbersold2 = 0;
    numbersold3 = 0;
    numbersold4 = 0;
    if sday == '' or eday == '' or smonth == '' or emonth == '':
        request.session['errormsg'] = 'Projection dates are not set correctly'
        return redirect('manufqty')
    sdate = date(2000,int(smonth),int(sday))
    edate = date(2000,int(emonth),int(eday))
    for record in SalesRecord.objects.all():
        if sdate > edate:
            sdate = sdate.replace(year=timezone.now().year-2)
            edate = edate.replace(year=timezone.now().year-1)
            if record.date > sdate and record.date < edate:
                numbersold1 = numbersold1 + record.cases_sold
            sdate = sdate.replace(year=timezone.now().year-3)
            edate = edate.replace(year=timezone.now().year-2)
            if record.date > sdate and record.date < edate:
                numbersold2 = numbersold2 + record.cases_sold
            sdate = sdate.replace(year=timezone.now().year-4)
            edate = edate.replace(year=timezone.now().year-3)
            if record.date > sdate and record.date < edate:
                numbersold3 = numbersold3 + record.cases_sold
            sdate = sdate.replace(year=timezone.now().year-5)
            edate = edate.replace(year=timezone.now().year-4)
            if record.date > sdate and record.date < edate:
                numbersold4 = numbersold4 + record.cases_sold
        else:
            if timezone.now().year-1 == record.date.year:
                sdate = sdate.replace(year=timezone.now().year-1)
                edate = edate.replace(year=timezone.now().year-1)
                if record.date > sdate and record.date < edate:
                    numbersold1 = numbersold1 + record.cases_sold
            if timezone.now().year-2 == record.date.year:
                sdate = sdate.replace(year=timezone.now().year-2)
                edate = edate.replace(year=timezone.now().year-2)
                if record.date > sdate and record.date < edate:
                    numbersold2 = numbersold2 + record.cases_sold
            if timezone.now().year-3 == record.date.year:
                sdate = sdate.replace(year=timezone.now().year-3)
                edate = edate.replace(year=timezone.now().year-3)
                if record.date > sdate and record.date < edate:
                    numbersold3 = numbersold3 + record.cases_sold
            if timezone.now().year-4 == record.date.year:
                sdate = sdate.replace(year=timezone.now().year-4)
                edate = edate.replace(year=timezone.now().year-4)
                if record.date > sdate and record.date < edate:
                    numbersold4 = numbersold4 + record.cases_sold
    data = dict()
    data['1 Year Ago'] = numbersold1
    data['2 Years Ago'] = numbersold2
    data['3 Years Ago'] = numbersold3
    data['4 Years Ago'] = numbersold4
    dave = (numbersold1+numbersold2+numbersold3+numbersold4)/4
    stdev = math.sqrt(((numbersold1-dave)**2 + (numbersold2-dave)**2 + (numbersold3-dave)**2 + (numbersold4-dave)**2)/4)
    dave = int(round(dave,0))
    stdev = round(stdev,1)
    data['Average'] = dave
    data['Std Dev'] = stdev
    if request.method == 'POST':    
        request.session['projection_autofill_value'] = dave
        request.session['projection_autofill_pk'] = pk
        return redirect('manufqty')
    context = {
        'data_table': data,
        'sku': sku.name
    }
    return render(request, 'manufacturing_goals/projection.html', context)

def set_project_date(request):
    request.session['start_day'] = request.POST['sday']
    request.session['start_month'] = request.POST['smonth']
    request.session['end_day'] = request.POST['eday']
    request.session['end_month'] = request.POST['emonth']
    return redirect('manufqty')
