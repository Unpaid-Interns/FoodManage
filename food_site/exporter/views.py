from django.shortcuts import render
from django.http import HttpResponse
from exporter import CSVExportTester

# Create your views here.
def index(request):
	CSVExportTester.run()
	return HttpResponse("This is the export view.")