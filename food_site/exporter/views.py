from django.shortcuts import render
from django.http import HttpResponse
from exporter import CSVTester

# Create your views here.
def index(request):
	CSVTester.run()
	return HttpResponse("This is the export view.")