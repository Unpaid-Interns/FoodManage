import csv
# from sku_manage import models

headerDict = {
    "skus.csv": ["Number", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Number", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formula.csv": ["SKU Number", "Ingredient Number", "Quantity"]
}

validFilePrefixes = ["skus", "ingredients", "product_lines", "formula"]


class CSVExport():
    def __init__(self):
        pass

    def export_to_csv(self, filename, data):
        export_csv(filename, data)


def export_csv(filename, data):
    with open("exporter/" + filename + ".csv", 'w', newline='') as csvfile:
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
            if filename.startswith("formula"):
                exportData.append(item.sku.name)
                exportData.append(item.ingredient.name)
                exportData.append(str(item.quantity))
            if len(exportData) > 0:
                dataWriter.writerow(exportData)


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
