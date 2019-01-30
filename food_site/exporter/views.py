from django.shortcuts import render
from django.http import HttpResponse
from exporter import CSVExport
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from sku_manage import models


# Create your views here.
def index(request):
    # CSVExportTester.batch_export()
    # return HttpResponse("This is the export view.")
    return download_line(request)


def download_line(request):
    batch_export()
    fs = FileSystemStorage('exporter/exports/')
    response = FileResponse(fs.open('foodmanage.zip', 'rb'), content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="foodmanage.zip"'
    return response

def batch_export():
    exporter = CSVExport.CSVExport()
    exporter.export_to_csv("skus", models.SKU.objects.all())
    exporter.export_to_csv("ingredients", models.Ingredient.objects.all())
    exporter.export_to_csv("product_lines", models.ProductLine.objects.all())
    exporter.export_to_csv("formulas", models.IngredientQty.objects.all())
    exporter.zip_export()
