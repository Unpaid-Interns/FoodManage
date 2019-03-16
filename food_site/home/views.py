from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
import requests
from django.contrib.auth.models import User

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

def help(request):
	return render(request, 'home/help.html', context=None)

def aboutus(request):
	return render(request, 'home/aboutus.html', context=None)

def authout(request):
        logout(request)
        return redirect('/')

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

def assistant(request):
	toSend = request.POST['message']
	if 'story' in toSend or toSend == 'DJANGO':
		return redirect('/aboutus')
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

def cya(request):
	request.session['cya'] = True
	return render(request, 'home/index.html', {'animate': True})

def cya_end(request):
	request.session['cya'] = False
	return render(request, 'home/victory.html', context=None)

def authmid(request):
	return render(request, 'home/test.html', context=None)
