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
        parsing_completed_successfully = True
        import_completed_successfully = False
        total_num_records_imported = 0
        for filename in self.filenames:
            file_prefix, valid = prefix_check(filename)
            if (valid):
                data, num_records, success, error_message = parser(filename)
                if (success):
                    total_num_records_imported += num_records
                    self.data_dict[file_prefix] = data
                    self.number_records_dict[file_prefix] = num_records
                else:
                    return False, "Import failed for: " + filename + "\n" + error_message
                    # print("Import failed for: " + filename)
                    # print(error_message)
                    # parsing_completed_successfully = False
            else:
                return False, "Import failed for: " + filename + "\n" + "ERROR: file name " + filename + " is invalid, must begin with valid prefix 'skus', \
                        'ingredients', 'product_lines', or 'sku_ingredients'"
                # print("Import failed for: " + filename)
                # print("ERROR: file name " + filename + " is invalid, must begin with valid prefix 'skus', \
                #         'ingredients', 'product_lines', or 'sku_ingredients'")
                # parsing_completed_successfully = False
        if parsing_completed_successfully:
            commit_success_message = self.commit_to_database()
            if commit_success_message == "":
                import_completed_successfully = True
            else:
                return False, commit_success_message
                # print("Import failed for: " + filename)
                # print(commit_success_message)
            if import_completed_successfully:
                return True, "IMPORT COMPLETED SUCCESSFULLY WITH #" + str(total_num_records_imported) \
                       + " RECORDS IMPORTED."
                # print("IMPORT COMPLETED SUCCESSFULLY WITH #" + str(num_records) + " RECORDS IMPORTED.")
        return import_completed_successfully, ""

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
        product_line_dict = dict()
        for i in self.data_dict["product_lines"]:
            models_array.append(i.convert_to_database_model())
            product_line_dict[i.name] = i.convert_to_database_model()
        product_lines_array = models_array.copy()

        models_array.clear()
        for i in self.data_dict["skus"]:
            valid_product_line_local = False
            valid_product_line_database = False
            chosen_product_line = None

            if i.product_line in product_line_dict:
                valid_product_line_local = True
                chosen_product_line = product_line_dict[i.product_line]

            temp_product_name_list = models.ProductLine.objects.filter(name=i.product_line)
            if len(temp_product_name_list) > 0:
                valid_product_line_database = True
                chosen_product_line = temp_product_name_list[0]

            valid_product_line = valid_product_line_database or valid_product_line_local

            if not valid_product_line:
                return ("Import failed for SKU CSV file \nERROR: Product Line name '" + i.product_line
                        + "' in SKU CSV file is not a valid name. It is not in the database "
                          "or in the product_lines CSV file attempting to be imported.")
            models_array.append(i.convert_to_database_model(chosen_product_line))
        sku_array = models_array.copy()

        models_array.clear()
        for i in self.data_dict["ingredients"]:
            models_array.append(i.convert_to_database_model())
        ingredients_array = models_array.copy()

        models_array.clear()
        for i in self.data_dict["formula"]:
            chosen_sku = None
            chosen_ingredient = None

            # check if sku_number for i is in database
            sku_number_in_database = False
            temp_sku_list = models.SKU.objects.filter(sku_num=int(i.sku_number))
            if len(temp_sku_list) > 0:
                sku_number_in_database = True
                chosen_sku = temp_sku_list[0]

            # check if sku_number for i is in to-be-imported stuff
            sku_number_in_local = False
            for sku in sku_array:
                if str(sku.sku_num) == i.sku_number:
                    sku_number_in_local = True
                    chosen_sku = sku

            sku_number_valid = sku_number_in_local or sku_number_in_database

            if not sku_number_valid:
                return "Import failed for formula CSV file \nERROR: SKU Number '" + i.sku_number \
                       + "' in formula CSV file is invalid. It does not " \
                         "exist in either the database or the SKU CSV being imported."

            # check if ingredient_number for i is in database
            ingredient_number_in_database = False
            temp_ingredient_list = models.Ingredient.objects.filter(number=int(i.ingredient_number))
            if len(temp_ingredient_list) > 0:
                ingredient_number_in_database = True
                chosen_ingredient = temp_ingredient_list[0]

            # check if ingredient_number for i is in to-be-imported stuff
            ingredient_number_in_local = False
            for ing in ingredients_array:
                if str(ing.number) == i.ingredient_number:
                    ingredient_number_in_local = True
                    chosen_ingredient = ing

            ingredient_number_valid = ingredient_number_in_database or ingredient_number_in_local

            if not ingredient_number_valid:
                return "Import failed for formula CSV file \nERROR: Ingredient Number '" + i.ingredient_number \
                       + "' in formula CSV file is invalid. It does not " \
                         "exist in either the database or the Ingredient CSV being imported."
            models_array.append(i.convert_to_database_model(chosen_sku, chosen_ingredient))
        formula_array = models_array.copy()

        models.ProductLine.objects.bulk_create(product_lines_array)
        models.SKU.objects.bulk_create(sku_array)
        models.Ingredient.objects.bulk_create(ingredients_array)
        models.IngredientQty.objects.bulk_create(formula_array)

        return ""


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
    num_records_parsed = 0
    num_record_ignored = 0

    # Open the csv file, read only
    try:
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
                    return None, None, False, "HEADER INVALID: Terminating import...\n" + header_issue

                # Call appropriate helper method
                method_to_call = getattr(sys.modules[__name__], file_prefix + "_parser_helper")
                temp_data = method_to_call(row, num_records_parsed)
                if isinstance(temp_data, str):
                    return None, None, False, temp_data

                # Check for matching database records
                database_record_check = check_for_identical_record(temp_data, file_prefix, num_records_parsed)
                if (database_record_check == ""):
                    matching_check = check_for_match_name_or_id(temp_data, parsed_data, file_prefix, num_records_parsed)
                    if (matching_check == ""):
                        # parsed_data.append(temp_data, file_prefix)
                        parsed_data.append(temp_data)
                        num_records_parsed += 1
                    else:
                        return None, None, False, matching_check
                elif (database_record_check == "identical"):
                    num_records_parsed += 1
                    num_record_ignored += 1
                else:
                    return None, None, False, database_record_check
    except FileNotFoundError:
        return None, None, False, "*ERROR: Unable to open file: '" + filename + "'."
    return parsed_data, num_records_parsed - num_record_ignored, True, ""


def skus_parser_helper(row, num_records_imported):
    if len(row) != 8:
        print('hello')
        print(row)
        return ("ERROR: Problem with number of entries in SKU CSV file at row #" + str(num_records_imported + 2) +
                ", needs 8 entries but has either more or less")
    if(row[0] == ""):
        # TODO: FILL IN SKU NUMBER BY CALLING FUNCTION
        pass
    for i in range(1,8):
        if row[i] == "":
            return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_imported + 2) + " and col #"
                    + str(i+1) + ". Entry in this row/column is required but is blank.")
    return CSVData.SKUData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def ingredients_parser_helper(row, num_records_imported):
    if len(row) != 6:
        return ("ERROR: Problem with number of entries in Ingredients CSV file at row #" + str(
            num_records_imported + 2) +
                ", needs 6 entries but has either more or less")
    return CSVData.IngredientData(row[0], row[1], row[2], row[3], row[4], row[5])


def product_lines_parser_helper(row, num_records_imported):
    if len(row) != 1:
        return ("ERROR: Problem with number of entries in Product Lines CSV file at row #" + str(
            num_records_imported + 2)
                + ", needs 1 entries but has either more or less")
    return CSVData.ProductLineData(row[0])


def formula_parser_helper(row, num_records_imported):
    if len(row) != 3:
        return ("ERROR: Problem with number of entries in Formula CSV file at row #"
                + str(num_records_imported + 2) + ", needs 3 entries but has either more or less")
    return CSVData.SKUIngredientData(row[0], row[1], row[2])

def decimal_check():
    # TODO
    pass

def intenger_check():
    # TODO
    pass

def check_for_identical_record(record, file_prefix, number_records_imported):
    # Returns blank string if no identical record found
    # Could use filter to check for same name and ID but not other fields
    if (file_prefix != "formula" and file_prefix != "skus"):
        record_converted = record.convert_to_database_model()
    if (file_prefix == "skus"):
        record_converted = record.convert_to_database_model(models.ProductLine(name=record.product_line))
        models_list = models.SKU.objects.filter(name=record_converted.name)
        for item in models_list:
            if (item.name == record_converted.name and item.sku_num == record_converted.sku_num and
                    item.case_upc == record_converted.case_upc and item.unit_upc == record_converted.unit_upc
                    and item.unit_size == record_converted.unit_size and item.units_per_case ==
                    record_converted.units_per_case and item.product_line.name == record.product_line and
                    item.comment == record_converted.comment):
                return "identical"
        list2 = models.SKU.objects.filter(case_upc=record_converted.case_upc)
        list3 = models.SKU.objects.filter(sku_num=record_converted.sku_num)
        if (len(list2) > 0):
            return "ERROR: Conflicting SKU record found with Case UPC '" + record.case_upc \
                   + "' and SKU number '" + record.sku_number + "', in conflict with database entry with Case UPC '" \
                   + str(list2[0].case_upc) + "' and SKU number '" \
                   + str(list2[0].sku_num) + "' at line '" + str(number_records_imported + 2) + "' in the SKU CSV file."
        if (len(list3) > 0):
            return "ERROR: Conflicting SKU record found with Case UPC '" + record.case_upc \
                   + "' and SKU number '" + record.sku_number + "', in conflict with database entry with Case UPC '" \
                   + str(list3[0].case_upc) + "' and SKU number '" \
                   + str(list3[0].sku_num) + "' at line '" + str(number_records_imported + 2) + "' in the SKU CSV file."
    if (file_prefix == "ingredients"):
        models_list = models.Ingredient.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record_converted.name and item.number == record_converted.number
                    and item.vendor_info == record_converted.vendor_info and
                    item.package_size == record_converted.package_size and item.cost == record_converted.cost
                    and item.comment == record_converted.comment):
                return "identical"
        list2 = models.Ingredient.objects.filter(name=record_converted.name)
        list3 = models.Ingredient.objects.filter(number=record_converted.number)
        if (len(list2) > 0):
            return "ERROR: Conflicting Ingredient record found with name '" + record.name \
                   + "' and number '" + record.number + "', in conflict with database entry with name '" \
                   + list2[0].name + "' and number '" \
                   + str(list2[0].number) + "' at line '" + str(number_records_imported + 2) \
                   + "' in the Ingredient CSV file."
        if (len(list3) > 0):
            return "ERROR: Conflicting Ingredient record found with name '" + record.name \
                   + "' and number '" + record.number + "', in conflict with database entry with name '" \
                   + list3[0].name + "' and number '" \
                   + str(list3[0].number) + "' at line '" + str(number_records_imported + 2) \
                   + "' in the Ingredient CSV file."
    if (file_prefix == "product_lines"):
        models_list = models.ProductLine.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record_converted.name):
                return "identical"
        list2 = models.ProductLine.objects.filter(name=record_converted.name)
        if (len(list2) > 0):
            return "ERROR: Conflicting Product Line record found with name '" + list2[0].name \
                   + "' at line '" + str(number_records_imported + 2) \
                   + "' in the product_lines CSV file."
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
                       + str(row_num) + "' and '" + str(num_records_imported + 1) + "'"
            if (new_record.case_upc == record.case_upc):
                return "ERROR: Duplicate Case UPC number(s) '" + new_record.case_upc + "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 1) + "'"
        if (file_prefix == "ingredients"):
            if (new_record.name == record.name):
                return "ERROR: Duplicate name '" + new_record.name + "' in Ingredients CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 1) + "'"
            if (new_record.number == record.number):
                return "ERROR: Duplicate Ingredient number '" + new_record.number + \
                       "' in Ingredients CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported) + "'"
        if (file_prefix == "product_lines"):
            if (new_record.name == record.name):
                return "ERROR: Duplicate name '" + new_record.name + "' in Product Lines CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 1) + "'"
        if (file_prefix == "formula"):
            if (new_record.sku_number == record.sku_number and
                    new_record.ingredient_number == record.ingredient_number):
                return "ERROR: Matching SKU/Ingredient pairing '" + new_record.sku + " / " + new_record.ingredient \
                       + "' in Formula CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported + 1) + "'"
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
