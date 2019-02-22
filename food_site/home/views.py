from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
import requests
from django.contrib.auth.models import User

# Create your views here.
def index(request):
	return render(request, 'home/index.html', context=None)

def authin(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		response = redirect('/')
		return response
	else:
		response = redirect('/invalidlogin')
		return response

def invalidlogin(request):
	return render(request, 'home/invalidlogin.html', context=None)

def help(request):
	return render(request, 'home/help.html', context=None)

def authout(request):
        logout(request)
        response = redirect('/')
        return response

token = None

def netlog(request):
	request.method = "get"
	request.GET._mutable = True
	request.GET['response_type'] = 'token'
	request.GET['redirect_uri'] = 'http://152.3.53.33:8000/netret/'
	request.GET['scope'] = 'basic'
	request.GET['client_id'] = 'unpaid-interns-hypo-meals'	
	response = redirect('https://oauth.oit.duke.edu/oauth/authorize.php?client_id=unpaid-interns-hypo-meals&scope=basic&redirect_uri=http://152.3.53.33:8000/authmid/&response_type=token&state=7')
	token = request.GET.get('access_token', 'No access token found')
	return response

def netret(request):
	token = request.POST['token']
	purl = 'https://api.colab.duke.edu/identity/v1/?redirect_uri=http://152.3.53.33:8000/'
	headers = {'x-api-key': 'unpaid-interns-hypo-meals', 'Authorization': 'Bearer '+token}
	r = requests.get(purl, headers=headers)
	tr = r.json()
	v = request.user.username
	un = tr.get('firstName')+'_'+tr.get('netid')
	pw = tr.get('netid')+'teMporArySecurityMeasUUreDogesAlAdwhaLeTaLeYasGuD28ME'
	em = tr.get('mail')
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
			email = em
		)
		user.save( )
		user = authenticate(request, username = un, password=pw)
		login(request, user)
		return redirect('/')	
	return redirect('/invalidlogin')

def authmid(request):
	return render(request, 'home/test.html', context=None)
