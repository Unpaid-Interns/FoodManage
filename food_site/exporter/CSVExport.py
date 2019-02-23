import csv
from zipfile import ZipFile
from sku_manage import models
from django.http import HttpResponse
import os

headerDict = {
    "skus.csv": ["SKU#", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "PL Name",
                 "Formula#", "Formula factor", "ML Shortnames", "Rate", "Comment"],
    "ingredients.csv": ["Ingr#", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formulas.csv": ["Formula#", "Name", "Ingr#", "Quantity", "Comment"],
    "manufacturing_lines.csv": ["Name", "Shortname", "Comment"]
}

'''
    validFilePrefixes's contents can be changed but MUST remain in order of what was originally:
    skus, ingredients, product_lines, formulas
    with any additions being after those 4 (names of those 4 can be changed freely!
'''
validFilePrefixes = ["skus", "ingredients", "product_lines", "formulas", "manufacturing_lines"]


class CSVExport():
    def __init__(self):
        pass

    def batch_export(self):
        export_to_csv(validFilePrefixes[0], models.SKU.objects.all())
        export_to_csv(validFilePrefixes[1], models.Ingredient.objects.all())
        export_to_csv(validFilePrefixes[2], models.ProductLine.objects.all())
        export_to_csv(validFilePrefixes[3], models.IngredientQty.objects.all())

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
        if validFilePrefixes[0] in filename:
            exportData.append(str(item.sku_num))
            exportData.append(item.name)
            exportData.append(str(item.case_upc))
            exportData.append(str(item.unit_upc))
            exportData.append(item.unit_size)
            exportData.append(str(item.units_per_case))
            exportData.append(item.product_line.name)
            exportData.append(str(item.formula.number))
            exportData.append(str(item.formula_scale))
            exportData.append(get_ml_lines_string(item))
            exportData.append(str(item.mfg_rate))
            exportData.append(item.comment)
        if validFilePrefixes[1] in filename:
            exportData.append(str(item.number))
            exportData.append(item.name)
            exportData.append(item.vendor_info)
            exportData.append(str(item.package_size) + " " + str(item.package_size_units))
            exportData.append(str(item.cost))
            exportData.append(item.comment)
        if validFilePrefixes[2] in filename:
            exportData.append(item.name)
        if validFilePrefixes[3] in filename:
            ingredient_number_list, quantity_list = get_lists_for_formula(item)
            count = 0
            for ing_num in ingredient_number_list:
                exportData = []
                exportData.append(str(item.number))
                exportData.append(str(item.name))
                exportData.append(str(ing_num))
                exportData.append(str(quantity_list[count]))
                exportData.append(str(item.comment))
                count = count + 1
                dataWriter.writerow(exportData)
        if validFilePrefixes[4] in filename:
            exportData.append(item.name)
            exportData.append(item.shortname)
            exportData.append(item.comment)
        if len(exportData) > 0 and validFilePrefixes[3] not in filename:
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


def get_ml_lines_string(sku):
    ml_lines_string = ""
    ml_lines_from_database = models.SkuMfgLine.objects.filter(sku__sku_num=sku.sku_num)
    for ml_line in ml_lines_from_database:
        ml_lines_string = ml_lines_string + ml_line.mfg_line.shortname
        ml_lines_string = ml_lines_string + ","
    if ml_lines_string.endswith(","):
        ml_lines_string = ml_lines_string[0:len(ml_lines_string)-1]
    final_string = ml_lines_string
    return final_string


def get_lists_for_formula(formula):
    ingredient_num_list = []
    quantity_list = []
    ingredient_qty_from_database = models.IngredientQty.objects.filter(formula__number=formula.number)
    for ing_qty in ingredient_qty_from_database:
        ingredient_num_list.append(ing_qty.ingredient.number)
        quantity_list.append(ing_qty.quantity)
    return ingredient_num_list, quantity_list
