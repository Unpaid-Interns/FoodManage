from django.shortcuts import render
from background_task import background
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required
import requests
from django_tables2 import RequestConfig, paginators
from django.db.models import Q
from django.contrib.auth.models import User, Group
from sales.models import SalesRecord, Customer
from sales import tasks
from manufacturing_goals import models as mfg_models
from sku_manage import models as sku_models
from .tables import UserTable
from .models import PlantManager

# Create your views here.
def index(request):
	return render(request, 'home/index.html', context={'invalidlogin': False})

def authin(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return redirect('/')
	else:
		return redirect('/invalidlogin')

def invalidlogin(request):
	return render(request, 'home/index.html', context={'invalidlogin': True})

def authout(request):
	logout(request)
	return redirect('/')

@login_required
def help(request):
	return render(request, 'home/help.html', context=None)

@login_required
def aboutus(request):
	return render(request, 'home/aboutus.html', context=None)

@login_required
def privacy(request):
	return render(request, 'home/hypomealsrus.html', context=None)

@permission_required('auth.change_user')
def selectuser(request):
	queryset = User.objects.all()
	context = {
		'paginated': True,
		'keyword': '',
	}
	paginate = {
		'paginator_class': paginators.LazyPaginator,
		'per_page': 25,
	}

	if request.method == 'GET':
		if 'keyword' in request.GET:
			keyword = request.GET['keyword']
			queryset = queryset.filter(Q(username__icontains=keyword) | 
				Q(first_name__icontains=keyword) | 
				Q(last_name__icontains=keyword) | 
				Q(email__icontains=keyword) | 
				Q(groups__name__iexact=keyword))
			context['keyword'] = keyword

		if 'remove_pagination' in request.GET:
			paginate = False
			context['paginated'] = False

	table = UserTable(queryset)
	context['user_table'] = table
	RequestConfig(request, paginate=paginate).configure(table)
	return render(request, 'home/userlist.html', context)

@permission_required('auth.change_user')
def edituser(request, pk):
	user = User.objects.get(pk=pk)
	groups = Group.objects.all().exclude(name="Plant Manager")
	plantmanager_group = Group.objects.get(name="Plant Manager")

	mfglines = sku_models.ManufacturingLine.objects.all()
	mfglines_managed = sku_models.ManufacturingLine.objects.filter(plantmanager__isnull=False, plantmanager__user__pk=pk)

	if request.method == "POST":
		is_plantmanager = False
		for group in groups:
			if str(group.pk) in request.POST and group not in user.groups.all():
				user.groups.add(group)
			if str(group.pk) not in request.POST and group in user.groups.all():
				user.groups.remove(group)
		user.is_staff = False
		for group in user.groups.all():
			if group.name in ('Administrator', 'Product Manager'):
				user.is_staff = True
		user.save()
		for mfgline in mfglines:
			if mfgline.shortname in request.POST:
				is_plantmanager = True
			if mfgline.shortname in request.POST and mfgline not in mfglines_managed:
				print('adding ' + str(mfgline))
				pm = PlantManager(user=user, mfgline=mfgline)
				pm.full_clean()
				pm.save()
			if mfgline.shortname not in request.POST and mfgline in mfglines_managed:
				print('removing ' + str(mfgline))
				PlantManager.objects.filter(user=user, mfgline=mfgline).delete()
			if is_plantmanager and plantmanager_group not in user.groups.all():
				user.groups.add(plantmanager_group)
			if not is_plantmanager and plantmanager_group in user.groups.all():
				user.groups.remove(plantmanager_group)


		return redirect('selectuser')

	context = {
		'user': user,
		'group_list': groups,
		'mfgline_list': mfglines,
		'selected_mfglines': mfglines_managed,
	}
	return render(request, 'home/edituser.html', context)

token = None

def netlog(request):
	request.method = "get"
	request.GET._mutable = True
	request.GET['response_type'] = 'token'
	request.GET['redirect_uri'] = 'https://hypomeals.com/netret/'
	request.GET['scope'] = 'basic'
	request.GET['client_id'] = 'unpaid-interns-hypo-meals'	
	response = redirect('https://oauth.oit.duke.edu/oauth/authorize.php?client_id=unpaid-interns-hypo-meals&scope=basic&redirect_uri=https://hypomeals.com/authmid/&response_type=token&state=7')
	token = request.GET.get('access_token', 'No access token found')
	return response

def netret(request):
	token = request.POST['token']
	purl = 'https://api.colab.duke.edu/identity/v1/?redirect_uri=https://hypomeals.com/'
	headers = {'x-api-key': 'unpaid-interns-hypo-meals', 'Authorization': 'Bearer '+token}
	r = requests.get(purl, headers=headers)
	tr = r.json()
	v = request.user.username
	un = tr.get('firstName')+'_'+tr.get('netid')
	pw = tr.get('netid')+'teMporArySecurityMeasUUreDogesAlAdwhaLeTaLeYasGuD28ME'
	em = tr.get('mail')
	fn = tr.get('firstName')
	ln = tr.get('lastName')
	user = authenticate(request, username=un, password=pw)
	if user is not None:
		login(request, user)
		return redirect('/')
	while User.objects.filter(username=un).exists() and authenticate(request, username=un, password=pw) is None:
		un = un + '+'
	user = authenticate(request, username=un, password=pw)
	if user is not None:
		login(request, user)
		return redirect('/')
	else:
		user = User.objects.create_user(
			username = un,
			password = pw,
			email = em,
			first_name = fn,
			last_name = ln
		)
		user.save( )
		user = authenticate(request, username = un, password=pw)
		login(request, user)
		return redirect('/')	
	return redirect('/invalidlogin')

@login_required
def assistant(request):
	toSend = request.POST['message']
	if 'story' in toSend or toSend == 'DJANGO':
		return redirect('/aboutus')
	if 'choose' in toSend and 'adventure' in toSend:
		return redirect('/cya')
	if 'Choose' in toSend and 'adventure' in toSend:
		return redirect('/cya')
	if 'find' in toSend or 'see' in toSend or 'view' in toSend or 'show' in toSend or 'Show' in toSend or 'where' in toSend or 'Where' in toSend or 'access' in toSend:
		if 'sku' in toSend or 'SKU' in toSend:
			return redirect('SKU')
		if 'ingredient' in toSend:
			return redirect('Ingredient')
		if 'product' in toSend and 'line' in toSend:
			return redirect('ProductLine')
		if 'formula' in toSend:
			return redirect('formula')
		if 'manufacturing' in toSend and 'line' in toSend:
			return redirect('ManufacturingLine')
		if 'sales' in toSend and 'report' in toSend:
			return redirect('sales_report_select')
		if 'admin' in toSend:
			return redirect('/admin')
		if 'mapping' in toSend:
			return redirect('map_view')
		if 'timeline' in toSend or 'map' in toSend or 'schedule' in toSend:
			return redirect('timeline')
		if 'report' in toSend:
			return redirect('reporting')
	if 'upload' in toSend or 'import' in toSend:
		return redirect('simple_upload')
	if 'scrape' in toSend or 'Scrape' in toSend:
		tasks.scrape()
		reply = 'The sales records are being updated.'
		context = {
			'reply': reply,
		}
		return render(request, 'home/index.html', context)
	if 'clear' in toSend or 'Clear' in toSend:
		if 'sales' in toSend:
			SalesRecord.objects.all().delete()
			Customer.objects.all().delete()
			reply = 'Sales data is being cleared.'
			context = {
				'reply': reply,
			}
			return render(request, 'home/index.html', context)
	if 'company standards' in toSend:
		return redirect('privacy-policy')
	toSend.replace(' ','_')
	r = requests.get("https://assistant-food.herokuapp.com/?message="+toSend)
	reply = ''
	try:
		tr = r.json()
		reply = tr.get('reply')
		reply.replace('_',' ')
	except:
		reply = "I'm sorry, your inquiry is above my pay grade. Do you have any other questions?"
	context = {
		'reply': reply,
	}
	return render(request, 'home/index.html', context)	

@login_required
def cya(request):
	request.session['cya'] = True
	return render(request, 'home/index.html', {'animate': True})

@login_required
def cya_end(request):
	request.session['cya'] = False
	return render(request, 'home/victory.html', context=None)

def authmid(request):
	return render(request, 'home/test.html', context=None)
