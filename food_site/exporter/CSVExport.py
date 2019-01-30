import csv
from zipfile import ZipFile
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

    def export_to_csv(self, filename, data):
        with open("exporter/exports/" + filename + ".csv", 'w', newline='') as csvfile:
            dataWriter = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_prefix, valid = prefix_check(filename)
            dataWriter.writerow(headerDict[file_prefix + ".csv"])
            for item in data:
                exportData = []
                if filename.startswith("skus"):
                    exportData.append(str(item.sku_num))
                    exportData.append(item.name)
                    exportData.append(str(item.case_upc))
                    exportData.append(str(item.unit_upc))
                    exportData.append(item.unit_size)
                    exportData.append(str(item.units_per_case))
                    exportData.append(item.product_line.name)
                    exportData.append(item.comment)
                if filename.startswith("ingredients"):
                    exportData.append(str(item.number))
                    exportData.append(item.name)
                    exportData.append(item.vendor_info)
                    exportData.append(item.package_size)
                    exportData.append(str(item.cost))
                    exportData.append(item.comment)
                if filename.startswith("product_lines"):
                    exportData.append(item.name)
                if filename.startswith("formulas"):
                    exportData.append(item.sku.sku_num)
                    exportData.append(item.ingredient.number)
                    exportData.append(str(item.quantity))
                if len(exportData) > 0:
                    dataWriter.writerow(exportData)

    def zip_export(self, file_paths=[prefix + ".csv" for prefix in validFilePrefixes]):
        # from: https://www.geeksforgeeks.org/working-zip-files-python/

        # path to folder which needs to be zipped
        directory = 'exporter/exports/'

        # calling function to get all file paths in the directory
        #file_paths = get_all_file_paths(directory)
        file_paths = ["exporter/exports/" + path for path in file_paths]

        # printing the list of all files to be zipped
        print('Following files will be zipped:')
        for file_name in file_paths:
            print(file_name)

        # writing files to a zipfile
        with ZipFile('exporter/exports/foodmanage.zip', 'w') as zip:
            # writing each file one by one
            for file in file_paths:
                zip.write(file)

        print('All files zipped successfully!')


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


def get_all_file_paths(directory):
    # from: https://www.geeksforgeeks.org/working-zip-files-python/

    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths
    return file_paths
