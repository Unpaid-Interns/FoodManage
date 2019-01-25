from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import logout, authenticate, login

# Create your views here.
def index(request):
	return render(request, 'home/index.html', context=None)

def authin(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		response = redirect('')
		return response
	else:
		response = redirect('')
		return response

def authout(request):
	logout(request)
	response = redirect('')
	return response
