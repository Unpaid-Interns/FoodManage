import sys
import csv
from importer import CSVData
from sku_manage import models
from decimal import Decimal

# test = "skus"
# test = "ingredients"
# test = "product_lines"
# test = "formula"
# test = "skus-Jan-22-2019"
# test = "ALL"
test = "class_test"

headerDict = CSVData.headerDict


class CSVImport():
    def __init__(self, filename_array=[]):
        self.filenames = filename_array
        self.data_dict = dict()
        self.number_records_dict = dict()

    def parse(self):
        import_completed_successfully = True
        for filename in self.filenames:
            file_prefix, valid = prefix_check(filename)
            if (valid):
                data, num_records, success, error_message = parser(filename)
                if (success):
                    self.data_dict[file_prefix] = data
                    self.number_records_dict[file_prefix] = num_records
                else:
                    print("Import failed for: " + filename)
                    print(error_message)
                    import_completed_successfully = False
            else:
                print("Import failed for: " + filename)
                print("ERROR: file name " + filename + " is invalid, must begin with valid prefix 'skus', \
                        'ingredients', 'product_lines', or 'sku_ingredients'")
                import_completed_successfully = False
        if import_completed_successfully:
            self.commit_to_database()

    def add_filename(self, filename):
        self.filenames.append(filename)

    def remove_filename(self, filename_to_remove):
        temp_filenames = []
        for filename in self.filenames:
            if (filename != filename_to_remove):
                temp_filenames.append(filename)
        self.filenames = temp_filenames

    def clear_filenames(self):
        self.filenames = []

    def set_filenames(self, filename_array):
        self.filenames = filename_array

    def commit_to_database(self):
        models_array = []
        for i in self.data_dict["product_lines"]:
            models_array.append(i.convert_to_database_model())
        models.ProductLine.objects.bulk_create(models_array)

        models_array.clear()
        for i in self.data_dict["skus"]:
            models_array.append(i.convert_to_database_model())
        models.SKU.objects.bulk_create(models_array)
        sku_array = models_array

        models_array.clear()
        for i in self.data_dict["ingredients"]:
            models_array.append(i.convert_to_database_model())
        models.Ingredient.objects.bulk_create(models_array)
        ingredients_array = models_array

        models_array.clear()
        for i in self.data_dict["formula"]:
            models_array.append(i.convert_to_database_model(sku_array, ingredients_array))
        models.IngredientQty.objects.bulk_create(models_array)

        # for p in self.data_dict:
        #     models_array = []
        #     for i in self.data_dict[p]:
        #         models_array.append(i.convert_to_database_model())
        #     if (p == "skus"):
        #         models.SKU.objects.bulk_create(models_array)
        #     if (p == "ingredients"):
        #         models.Ingredient.objects.bulk_create(models_array)
        #     if (p == "product_lines"):
        #         models.ProductLine.objects.bulk_create(models_array)
        #     if (p == "formula"):
        #         models.IngredientQty.objects.bulk_create(models_array)


def parser(filename):
    # Returns: parsed data, number records imported, bool indicating success, and error message

    # Check for valid prefix in file name
    file_prefix, valid = prefix_check(filename)
    if not valid:
        print("FILE NAME INVALID: Terminating import...")
        return None, None, False, "ERROR: file name " + filename + " is invalid, must begin with valid prefix 'skus', \
        'ingredients', 'product_lines', or 'sku_ingredients'"

    # Initialize variables
    header_correct = headerDict[file_prefix + ".csv"]
    parsed_data = []
    num_records_imported = 0

    # Open the csv file, read only
    with open(filename, 'r') as csvfile:
        data_reader = csv.reader(csvfile, quotechar='|')
        header_valid = True
        header_check_complete = False
        header_issue = ""
        for row in data_reader:
            # Make sure header is correct
            if not header_check_complete:
                header_valid, header_issue = header_check(row, header_correct)
                header_check_complete = True
                continue
            if not header_valid:
                print("HEADER INVALID: Terminating import...")
                print(header_issue)
                return None, None, False, header_issue

            # Call appropriate helper method
            method_to_call = getattr(sys.modules[__name__], file_prefix + "_parser_helper")
            temp_data = method_to_call(row, num_records_imported)
            if isinstance(temp_data, str):
                return None, None, False, temp_data

            # Check for matching database records
            database_record_check = check_for_identical_record(temp_data, file_prefix)
            if (database_record_check == ""):
                matching_check = check_for_match_name_or_id(temp_data, parsed_data, file_prefix, num_records_imported)
                if (matching_check == ""):
                    # parsed_data.append(temp_data, file_prefix)
                    parsed_data.append(temp_data)
                    num_records_imported += 1
                else:
                    return None, None, False, matching_check
            elif (database_record_check == "identical"):
                pass
            else:
                return None, None, False, database_record_check
    return parsed_data, num_records_imported, True, ""


def skus_parser_helper(row, num_records_imported):
    if len(row) != 8:
        return ("ERROR: Problem with number of entries in SKU CSV file at row #" + (num_records_imported + 1) +
                ", needs 8 entries but has " + str(row.__len__))
    return CSVData.SKUData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def ingredients_parser_helper(row, num_records_imported):
    if len(row) != 6:
        return ("ERROR: Problem with number of entries in Ingredients CSV file at row #" + (num_records_imported + 1) +
                ", needs 6 entries but has " + str(row.__len__))
    return CSVData.IngredientData(row[0], row[1], row[2], row[3], row[4], row[5])


def product_lines_parser_helper(row, num_records_imported):
    if len(row) != 1:
        return ("ERROR: Problem with number of entries in Product Lines CSV file at row #" + (num_records_imported + 1)
                + ", needs 1 entries but has " + str(row.__len__))
    return CSVData.ProductLineData(row[0])


def formula_parser_helper(row, num_records_imported):
    if len(row) != 3:
        return ("ERROR: Problem with number of entries in Formula CSV file at row #"
                + (num_records_imported + 1) + ", needs 3 entries but has " + str(row.__len__))
    return CSVData.SKUIngredientData(row[0], row[1], row[2])


def check_for_identical_record(record, file_prefix):
    # Returns blank string if no identical record found
    # Could use filter to check for same name and ID but not other fields
    if(file_prefix != "formula"):
        record_converted = record.convert_to_database_model()
    if (file_prefix == "skus"):
        models_list = models.SKU.objects.filter(name=record_converted.name)
        for item in models_list:
            if (item.name == record_converted.name and item.sku_num == record_converted.sku_num and
                    item.case_upc == record_converted.case_upc and item.unit_upc == record_converted.unit_upc
                    and item.unit_size == record_converted.unit_size and item.units_per_case ==
                    record_converted.units_per_case and item.product_line == record_converted.product_line and
                    item.comment == record_converted.comment):
                return "identical"
        list2 = models.SKU.objects.filter(case_upc=record_converted.case_upc, sku_num=record_converted.sku_num)
        if (len(list2) > 0):
            return "ERROR: Non-identical conflicting SKU record found with Case UPC '" + list2[
                0].case_upc + "' and SKU number '" \
                   + str(list2[0].sku_num)
    if (file_prefix == "ingredients"):
        models_list = models.Ingredient.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record_converted.name and item.number == record_converted.number
                    and item.vendor_info == record_converted.vendor_info and
                    item.package_size == record_converted.package_size and item.cost == record_converted.cost
                    and item.comment == record_converted.comment):
                return "identical"
        list2 = models.Ingredient.objects.filter(name=record_converted.name, number=record_converted.number)
        if (len(list2) > 0):
            return "ERROR: Non-identical conflicting Ingredient record found with name '" + list2[0].name + \
                   "' and number '" + str(list2[0].number)
    if (file_prefix == "product_lines"):
        models_list = models.ProductLine.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record_converted.name):
                return "identical"
        list2 = models.ProductLine.objects.filter(name=record_converted.name)
        if (len(list2) > 0):
            return "ERROR: Non-identical conflicting Product Line record found with name '" + list2[0].name
    if (file_prefix == "formula"):
        models_list = models.IngredientQty.objects.filter(quantity=Decimal(record.quantity))
        for item in models_list:
            if (item.sku.sku_num == int(record.sku_number) and item.ingredient.number == int(record.ingredient_number)
                    and item.quantity == Decimal(record.quantity)):
                return "identical"
        # Do we need to check or non-identical match here?
    return ""


def check_for_match_name_or_id(new_record, record_list, file_prefix, num_records_imported):
    row_num = 0
    for record in record_list:
        row_num += 1
        if (file_prefix == "skus"):
            # if (new_record.name == record.name):
            #     return "ERROR: Duplicate name '" + new_record.name + "' in SKU CSV file at lines '" \
            #            + str(row_num) + "' and '" + str(num_records_imported+1) + "'"
            if (new_record.sku_number == record.sku_number):
                return "ERROR: Duplicate SKU number(s) '" + new_record.sku_number + "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported+1) + "'"
            if (new_record.case_upc == record.case_upc):
                return "ERROR: Duplicate Case UPC number(s) '" + new_record.case_upc + "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported+1) + "'"
        if (file_prefix == "ingredients"):
            if (new_record.name == record.name):
                return "ERROR: Duplicate name '" + new_record.name + "' in Ingredients CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported+1) + "'"
            if (new_record.number == record.number):
                return "ERROR: Duplicate Ingredient number '" + new_record.number + \
                       "' in Ingredients CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported) + "'"
        if (file_prefix == "product_lines"):
            if (new_record.name == record.name):
                return "ERROR: Duplicate name '" + new_record.name + "' in Product Lines CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported+1) + "'"
        if (file_prefix == "formula"):
            if (new_record.sku_number == record.sku_number and
                    new_record.ingredient_number == record.ingredient_number):
                return "ERROR: Matching SKU/Ingredient pairing '" + new_record.sku + " / " + new_record.ingredient \
                       + "' in Formula CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported+1) + "'"
    return ""


def header_check(header, headerCorrect):
    col = 0
    for item in header:
        if headerCorrect[col] != item:
            headerError = "ERROR: csv header = '" + item + "' but should be '" + headerCorrect[col] + "'"
            return False, headerError
        col += 1
    return True, ""


def prefix_check(filename):
    filename_no_importer_prefix = filename
    if filename.startswith("importer/"):
        filename_no_importer_prefix = filename[len("importer/"):]
    file_prefix = ""
    valid = True
    for prefix in CSVData.validFilePrefixes:
        if filename_no_importer_prefix.startswith(prefix):
            file_prefix = prefix
    if (file_prefix == ""):
        valid = False
    return file_prefix, valid

"""
Testing code to run if code executed directly.

Uncomment desired test to run at top of code.
"""
if __name__ == '__main__':
    if (test == "ALL"):
        print("IMPORT ALL TEST STARTING...")
        data = []
        numRecordsImported = []
        for prefix in CSVData.validFilePrefixes:
            tempData, tempNumRecords = parser(prefix + ".csv")
            data.append(tempData)
            numRecordsImported.append(tempNumRecords)
        try:
            count = 0
            for imported_set in data:
                print(type(data[count][0]).__name__)
                print("Number of records imported = ", numRecordsImported[count])
                for item in data[count]:
                    print(item)
                print("")
                count += 1
        except UnicodeError:
            print("error printing data")
    elif (test == "class_test"):
        print("CLASS TEST STARTING...")
        importer = CSVImport()
        filenames = ["skus.csv", "ingredients.csv", "product_lines.csv", "sku_ingredients.csv"]
        importer.set_filenames(filenames)
        importer.parse()
        try:
            for file_prefix in importer.data_dict:
                print("Data for: " + file_prefix + ".csv")
                print("Number of records imported = ", importer.number_records_dict[file_prefix])
                for item in importer.data_dict[file_prefix]:
                    print(item)
                print("")
        except UnicodeError:
            print("error printing data")
    else:
        print("IMPORT TEST STARTING FOR: " + test + "...")
        data, numRecordsImported = parser(test + ".csv")
        try:
            print("Number of records imported = ", numRecordsImported)
            for item in data:
                print(item)
        except UnicodeError:
            print("error printing data")
