import csv
from zipfile import ZipFile
from sku_manage import models
from django.http import HttpResponse
import os

headerDict = {
    "skus.csv": ["SKU#", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Ingr#", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formulas.csv": ["SKU#", "Ingr#", "Quantity"]
}

validFilePrefixes = ["skus", "ingredients", "product_lines", "formulas"]


class CSVExport():
    def __init__(self):
        pass

    def batch_export(self):
        export_to_csv("skus", models.SKU.objects.all())
        export_to_csv("ingredients", models.Ingredient.objects.all())
        export_to_csv("product_lines", models.ProductLine.objects.all())
        export_to_csv("formulas", models.IngredientQty.objects.all())

    def zip_export(self, file_paths=[prefix + ".csv" for prefix in validFilePrefixes]):
        # from: https://www.geeksforgeeks.org/working-zip-files-python/

        # path to folder which needs to be zipped
        directory = 'exporter/exports/'

        # calling function to get all file paths in the directory
        # file_paths = get_all_file_paths(directory)
        file_paths = ["exporter/exports/" + path for path in file_paths]

        # printing the list of all files to be zipped
        # print('Following files will be zipped:')
        # for file_name in file_paths:
        #     print(file_name)

        # writing files to a zipfile
        with ZipFile('exporter/exports/foodmanage.zip', 'w') as zip:
            # writing each file one by one
            remove_file_list = []
            for file in file_paths:
                zip.write(file)
                remove_file_list.append(file)
            for file in remove_file_list:
                os.remove(file)

        # print('All files zipped successfully!')


def export_to_csv(filename, data):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
    dataWriter = csv.writer(response)
    file_prefix, valid = prefix_check(filename)
    dataWriter.writerow(headerDict[file_prefix + ".csv"])
    for item in data:
        exportData = []
        if "skus" in filename:
            exportData.append(str(item.sku_num))
            exportData.append(item.name)
            exportData.append(str(item.case_upc))
            exportData.append(str(item.unit_upc))
            exportData.append(item.unit_size)
            exportData.append(str(item.units_per_case))
            exportData.append(item.product_line.name)
            exportData.append(item.comment)
        if "ingredients" in filename:
            exportData.append(str(item.number))
            exportData.append(item.name)
            exportData.append(item.vendor_info)
            exportData.append(item.package_size)
            exportData.append(str(item.cost))
            exportData.append(item.comment)
        if "product_lines" in filename:
            exportData.append(item.name)
        if "formulas" in filename:
            exportData.append(item.sku.sku_num)
            exportData.append(item.ingredient.number)
            exportData.append(str(item.quantity))
        if len(exportData) > 0:
            dataWriter.writerow(exportData)
    return response


def prefix_check(filename):
    filename_no_importer_prefix = filename
    if filename.startswith("importer/"):
        filename_no_importer_prefix = filename[len("importer/"):]
    file_prefix = ""
    valid = True
    for prefix in validFilePrefixes:
        if filename_no_importer_prefix.startswith(prefix):
            file_prefix = prefix
    if file_prefix == "":
        valid = False
    return file_prefix, valid
