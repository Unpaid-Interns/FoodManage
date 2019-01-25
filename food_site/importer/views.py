from django.shortcuts import render
from django.http import HttpResponse
from importer import CSVImportTester

# Create your views here.
def index(request):
	CSVImportTester.run()
	return HttpResponse("This is the import view.")