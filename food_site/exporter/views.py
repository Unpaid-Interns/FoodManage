from django.shortcuts import render
from django.http import HttpResponse
from exporter import CSVExport
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
import os


# Create your views here.
def index(request):
    # CSVExportTester.batch_export()
    # return HttpResponse("This is the export view.")
    return download_line(request)


def download_line(request):
    exporter = CSVExport.CSVExport()
    exporter.batch_export()
    fs = FileSystemStorage('exporter/exports/')
    response = FileResponse(fs.open('foodmanage.zip', 'rb'), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="foodmanage.zip"'
    return response
