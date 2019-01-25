from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect

# Create your views here.
def index(request):
	return render(request, 'home/index.html', context=None)

def authin(request):
	username = request.GET['username']
	password = request.GET['password']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		response = redirect('/admin')
		return response
	else:
		response = redirect('/invalidlogin')
		return response

def authout(request):
	logout(request)
	response = redirect('/')
	return response

def invalidlogin(request):
	return render(request, 'home/invalidlogin.html', context=None)
