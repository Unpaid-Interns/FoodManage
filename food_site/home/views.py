from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
def index(request):
	return render(request, 'home/index.html', context=None)
