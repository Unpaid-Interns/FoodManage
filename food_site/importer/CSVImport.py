import sys
import csv
from importer import CSVData
from sku_manage import models
from decimal import Decimal

headerDict = CSVData.headerDict


class CSVImport:
    def __init__(self, filename_array=[]):
        self.filenames = filename_array
        self.data_dict = dict()
        self.conflict_dict = dict()
        self.number_records_dict = dict()
        self.file_prefix_array = []
        self.total_num_records_imported = 0
        self.total_num_records_ignored = 0
        self.total_num_records_conflict = 0

    def parse(self):
        """
        Parses the data
        :return: bool for success/failure, error str
        """
        parsing_completed_successfully = True
        import_completed_successfully = False
        for filename in self.filenames:
            file_prefix, valid = prefix_check(filename)
            if (valid):
                self.file_prefix_array.append(file_prefix)
                data, conflict_data, num_records, num_ignored, num_conflict, success, error_message = parser(filename)
                if (success):
                    self.total_num_records_imported += num_records
                    self.total_num_records_ignored += num_ignored
                    self.total_num_records_conflict += num_conflict
                    self.data_dict[file_prefix] = data
                    if len(conflict_data) > 0:
                        self.conflict_dict[file_prefix] = conflict_data
                    self.number_records_dict[file_prefix] = num_records
                else:
                    return False, "Import failed for: " + filename + ". \n" + error_message
                    # print("Import failed for: " + filename)
                    # print(error_message)
                    # parsing_completed_successfully = False
            else:
                return False, "Import failed for: " + filename + ". \n" + "ERROR: file name " + filename \
                       + " is invalid, must begin with valid prefix 'skus', \
                        'ingredients', 'product_lines', or 'sku_ingredients'"
                # print("Import failed for: " + filename)
                # print("ERROR: file name " + filename + " is invalid, must begin with valid prefix 'skus', \
                #         'ingredients', 'product_lines', or 'sku_ingredients'")
                # parsing_completed_successfully = False
        if parsing_completed_successfully:
            if not self.conflict_dict:
                commit_success_message = self.commit_to_database()
                if commit_success_message == "":
                    import_completed_successfully = True
                else:
                    return False, commit_success_message
                    # print("Import failed for: " + filename)
                    # print(commit_success_message)
                if import_completed_successfully:
                    return True, "Import completed successfully with #" + str(self.total_num_records_imported) \
                           + " records imported and #" + str(self.total_num_records_ignored) \
                           + " records ignored and #" + str(self.total_num_records_conflict) + " records in conflict."
            else:
                return False, "Conflicts exist. Please confirm how to handle them below."
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

    def add_data_to_commit_dict(self, file_prefix, data):
        self.data_dict[file_prefix] = data

    def make_serializable_conflict_dict(self):
        serializable_dict = dict()
        for file_prefix in self.conflict_dict:
            new_conflict_records_list = []
            conflict_records_list = self.conflict_dict[file_prefix]
            for conflict_tuple in conflict_records_list:
                data = conflict_tuple[0]
                message = conflict_tuple[2]
                new_conflict_records_list.append([data.convert_to_string_array(), message])
            serializable_dict[file_prefix] = new_conflict_records_list
        return serializable_dict

    def get_conflict_dict_from_serializable(self, serializable_dict):
        original_dict = dict()
        for file_prefix in serializable_dict:
            new_conflict_records_list = []
            conflict_records_list = serializable_dict[file_prefix]
            for conflict_tuple in conflict_records_list:
                data_string_array = conflict_tuple[0]
                message = conflict_tuple[1]
                data = None
                if len(data_string_array) == 8:
                    data = CSVData.SKUData(data_string_array[0], data_string_array[1], data_string_array[2],
                                           data_string_array[3], data_string_array[4], data_string_array[5],
                                           data_string_array[6], data_string_array[7])
                elif len(data_string_array) == 6:
                    data = CSVData.IngredientData(data_string_array[0], data_string_array[1], data_string_array[2],
                                           data_string_array[3], data_string_array[4], data_string_array[5])
                elif len(data_string_array) == 1:
                    data = CSVData.ProductLineData(data_string_array[0])
                elif len(data_string_array) == 3:
                    data = CSVData.SKUIngredientData(data_string_array[0], data_string_array[1], data_string_array[2])
                if data is None:
                    return original_dict
                case_upc_conflicts = models.SKU.objects.filter(case_upc=Decimal(data.case_upc))
                sku_num_conflicts = models.SKU.objects.filter(sku_num=int(data.sku_number))
                conflict_database_data = None
                if (len(case_upc_conflicts) > 0):
                    conflict_database_data = case_upc_conflicts[0]
                elif (len(sku_num_conflicts) > 0):
                    conflict_database_data = sku_num_conflicts[0]
                if conflict_database_data is None:
                    return original_dict
                new_conflict_records_list.append([data, conflict_database_data, message])
            original_dict[file_prefix] = new_conflict_records_list
        return original_dict



    def commit_to_database(self):
        """
        Commits data to database
        :return: error str (blank string if no error)
        """

        models_array = []
        product_line_dict = dict()
        if "product_lines" in self.file_prefix_array:
            for i in self.data_dict["product_lines"]:
                models_array.append(i.convert_to_database_model())
                product_line_dict[i.name] = i.convert_to_database_model()
        product_lines_array = models_array.copy()
        models_array.clear()

        skus_that_need_numbers = []
        skus_num_list = []
        if "skus" in self.file_prefix_array:
            for i in self.data_dict["skus"]:
                success, chosen_product_line_or_error_message = choose_product_line(i, product_line_dict)
                if not success:
                    return chosen_product_line_or_error_message
                if i.sku_number != "-1":
                    skus_num_list.append(int(i.sku_number))
                    models_array.append(i.convert_to_database_model(chosen_product_line_or_error_message))
                else:
                    skus_that_need_numbers.append(i)
            for s in models.SKU.objects.all():
                skus_num_list.append(int(s.sku_num))
            skus_num_list.sort()
            for s in skus_that_need_numbers:
                chosen_num = -1
                for index in range(0, len(skus_num_list)-1):
                    if chosen_num != -1:
                        continue
                    if skus_num_list[index] + 1 != skus_num_list[index + 1]:
                        chosen_num = skus_num_list[index] + 1
                        skus_num_list.append(chosen_num)
                        skus_num_list.sort()
                        # print("Chosen number for SKU = " + str(chosen_num))
                if chosen_num == -1:
                    chosen_num = skus_num_list[len(skus_num_list)-1] + 1
                    skus_num_list.append(chosen_num)
                    skus_num_list.sort()
                s.sku_number = chosen_num
                success, chosen_product_line_or_error_message = choose_product_line(s, product_line_dict)
                if not success:
                    return chosen_product_line_or_error_message
                models_array.append(s.convert_to_database_model(chosen_product_line_or_error_message))
        sku_array = models_array.copy()
        models_array.clear()

        ingredients_that_need_numbers = []
        ingr_nums_list = []
        if "ingredients" in self.file_prefix_array:
            for i in self.data_dict["ingredients"]:
                if i.number != "-1":
                    ingr_nums_list.append(int(i.number))
                    models_array.append(i.convert_to_database_model())
                else:
                    # print("-1 DETECTED!")
                    ingredients_that_need_numbers.append(i)
            for i in models.Ingredient.objects.all():
                ingr_nums_list.append(int(i.number))
            ingr_nums_list.sort()
            for i in ingredients_that_need_numbers:
                chosen_num = -1
                for index in range(0, len(ingr_nums_list)):
                    if chosen_num != -1:
                        continue
                    if ingr_nums_list[index]+1 != ingr_nums_list[index+1]:
                        chosen_num = ingr_nums_list[index]+1
                        ingr_nums_list.append(chosen_num)
                        ingr_nums_list.sort()
                        # print("Chosen number for Ingr = " + str(chosen_num))
                if chosen_num == -1:
                    chosen_num = ingr_nums_list[len(ingr_nums_list)-1] + 1
                    ingr_nums_list.append(chosen_num)
                    ingr_nums_list.sort()
                i.number = str(chosen_num)
                models_array.append(i.convert_to_database_model())
        ingredients_array = models_array.copy()
        models_array.clear()

        if "formulas" in self.file_prefix_array:
            for i in self.data_dict["formulas"]:
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
                    return "Import failed for formulas CSV file. \nERROR: SKU Number '" + i.sku_number \
                           + "' in formulas CSV file is invalid. It does not " \
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
                    return "Import failed for formulas CSV file. \nERROR: Ingredient Number '" + i.ingredient_number \
                           + "' in formulas CSV file is invalid. It does not " \
                             "exist in either the database or the Ingredient CSV being imported."
                models_array.append(i.convert_to_database_model(chosen_sku, chosen_ingredient))

        formula_array = models_array.copy()

        models.ProductLine.objects.bulk_create(product_lines_array)
        models.SKU.objects.bulk_create(sku_array)
        models.Ingredient.objects.bulk_create(ingredients_array)
        models.IngredientQty.objects.bulk_create(formula_array)

        return ""


def parser(filename):
    """
    Parses the given file
    :param filename: str of file's name
    :return: parsed data, number records imported, bool indicating success, and error message string
    """

    # Check for valid prefix in file name
    file_prefix, valid = prefix_check(filename)
    if not valid:
        print("FILE NAME INVALID: Terminating import... ")
        return None, None, None, None, None, False, "ERROR: file name " + filename + " is invalid, must begin with valid prefix 'skus', \
        'ingredients', 'product_lines', or 'sku_ingredients'"

    # Initialize variables
    header_correct = headerDict[file_prefix + ".csv"]
    parsed_data = []
    conflicting_records_tpl = []
    num_records_parsed = 0
    num_record_ignored = 0
    num_record_conflicted = 0

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
                    header_valid, header_issue = header_check(row, header_correct, file_prefix)
                    header_check_complete = True
                    continue
                if not header_valid:
                    return None, None, None, None, None, False, \
                           "HEADER INVALID: Terminating import... \n" + header_issue

                # Call appropriate helper method
                method_to_call = getattr(sys.modules[__name__], file_prefix + "_parser_helper")
                temp_data = method_to_call(row, num_records_parsed)
                if isinstance(temp_data, str):
                    return None, None, None, None, None, False, temp_data

                # Check for matching database records
                matching_check = check_for_match_name_or_id(temp_data, parsed_data, file_prefix, num_records_parsed)
                if (matching_check == ""):
                    database_record_check, conflicting_database_model = check_for_identical_record(temp_data, file_prefix, num_records_parsed)
                    if (database_record_check == ""):
                        # parsed_data.append(temp_data, file_prefix)
                        parsed_data.append(temp_data)
                        num_records_parsed += 1
                    elif (database_record_check == "identical"):
                        num_records_parsed += 1
                        num_record_ignored += 1
                    elif ("CONFLICT:" in database_record_check):
                        # TODO: Marking this as WIP
                        conflicting_records_tpl.append([temp_data, conflicting_database_model, database_record_check])
                        num_records_parsed += 1
                        num_record_conflicted += 1
                    else:
                        return None, None, None, None, None, False, database_record_check
                else:
                    return None, None, None, None, None, False, matching_check
    except FileNotFoundError:
        return None, None, None, None, None, False, "*ERROR: File not found. Unable to open file: '" + filename + "'."
    except:
        return None, None, None, None, None, False, "*ERROR: File type not valid or unknown error."
    return parsed_data, conflicting_records_tpl, num_records_parsed - num_record_ignored - num_record_conflicted\
        , num_record_ignored, num_record_conflicted, True, ""


def skus_parser_helper(row, num_records_parsed):
    """
    Helper function for skus.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != 8:
        print('hello')
        print(row)
        return ("ERROR: Problem with number of entries in SKU CSV file at row #" + str(num_records_parsed + 2) +
                ", needs 8 entries but has either more or less.")
    if(row[0] == ""):
        row[0] = "-1"
    else:
        if not integer_check(row[0]):
            return "ERROR: SKU# in SKU CSV file is not an integer in row #" + str(num_records_parsed + 2) \
                   + "and col #1."
    for i in range(1,7):
        if row[i] == "":
            return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                    + str(i+1) + ". Entry in this row/column is required but is blank.")
        if i in [2,3]:
            if not decimal_check(row[i]):
                return("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                      + str(i + 1) + ". Entry in this row/column is required to be a decimal value but is not.")
            if i == 2:
                # TODO: Check case_upc validity (might have to do this in commit area instead...)
                pass
            if i == 3:
                # TODO: Check unit_upc validity (might have to do this in commit area instead...)
                pass
        if i in [5]:
            if not integer_check(row[i]):
                return("ERROR: Problem with 'Count per case' in SKU CSV file in row #" + str(num_records_parsed + 2)
                       + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a integer value "
                                                     "but is not.")
    return CSVData.SKUData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def ingredients_parser_helper(row, num_records_parsed):
    """
    Helper function for ingredient.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != 6:
        return ("ERROR: Problem with number of entries in Ingredients CSV file at row #" + str(
            num_records_parsed + 2) +
                ", needs 6 entries but has either more or less.")
    if (row[0] == ""):
        row[0] = "-1"
    else:
        if not integer_check(row[0]):
            return "ERROR: Ingr# in Ingredient CSV file is not an integer in row #" \
                   + str(num_records_parsed + 2) + "and col #1."
    for i in [1, 3, 4]:
        if row[i] == "":
            return ("ERROR: Problem in Ingredient CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                    + str(i+1) + ". Entry in this row/column is required but is blank.")
        if i in [4]:
            if not decimal_check(row[i]):
                return("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                       + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a decimal value "
                                                     "but is not.")
    return CSVData.IngredientData(row[0], row[1], row[2], row[3], row[4], row[5])


def product_lines_parser_helper(row, num_records_parsed):
    """
    Helper function for product_lines.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != 1:
        return ("ERROR: Problem with number of entries in Product Lines CSV file at row #" + str(
            num_records_parsed + 2)
                + ", needs 1 entries but has either more or less.")
    return CSVData.ProductLineData(row[0])


def formulas_parser_helper(row, num_records_parsed):
    """
    Helper function for formulas.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != 3:
        return ("ERROR: Problem with number of entries in Formulas CSV file at row #"
                + str(num_records_parsed + 2) + ", needs 3 entries but has either more or less.")
    for i in [0, 1, 2]:
        if i in [0,1]:
            if not integer_check(row[i]):
                return "ERROR: Problem in Formulas CSV file in row #" + str(num_records_parsed + 2) + " and col #" \
                    + str(i+1) + ". Entry in this column must be an integer value but is not."
        if i in [2]:
            if not decimal_check(row[i]):
                return "ERROR: Problem in Formulas CSV file with 'Quantity' in row #" + str(num_records_parsed + 2) \
                       + " and col #" \
                       + str(i + 1) + ". Entry in this column must be an decimal value but is not."
    return CSVData.SKUIngredientData(row[0], row[1], row[2])


def decimal_check(numberString):
    """
    Checks if a string can be converted to a decimal
    :param numberString: str input to be checked as a decimal
    :return: True/False to indicate if it is/is not a decimal
    """
    try:
        _ = Decimal(numberString)
        return True
    except:
        return False


def integer_check(numberString):
    """
    Checks if a string can be converted to an integer
    :param numberString: str input to be checked as an integer
    :return: True/False to indicate if it is/is not an integer
    """
    try:
        _ = int(numberString)
        return True
    except:
        return False


def check_for_identical_record(record, file_prefix, number_records_imported):
    """
    Checks for identical and/or conflicting records in the database
    :param record: The record being parsed
    :param file_prefix: The prefix to the file being imported
    :param number_records_imported: The number of records imported so far
    :return: str with the error if there is one
    """
    # Returns blank string if no identical record found
    # Could use filter to check for same name and ID but not other fields
    if (file_prefix != "formulas" and file_prefix != "skus"):
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
                return "identical", None
            elif (item.name == record_converted.name and record_converted.sku_num == -1 and
                    item.case_upc == record_converted.case_upc and item.unit_upc == record_converted.unit_upc
                    and item.unit_size == record_converted.unit_size and item.units_per_case ==
                    record_converted.units_per_case and item.product_line.name == record.product_line and
                    item.comment == record_converted.comment):
                return "identical", None
        list2 = models.SKU.objects.filter(case_upc=record_converted.case_upc)
        list3 = models.SKU.objects.filter(sku_num=record_converted.sku_num)
        if (len(list2) > 0):
            # TODO: Ask user for override.
            return "CONFLICT: Conflicting SKU record found with name '" + record.name + "' and Case UPC '" \
                   + record.case_upc \
                   + "', in conflict with database entry with name '" \
                   + list2[0].name + "' and Case UPC '" \
                   + str(list2[0].case_upc) + \
                   "' at line '" + \
                   str(number_records_imported + 2) + "' in the SKU CSV file.", list2[0]
        if (len(list3) > 0):
            # TODO: Ask user for override.
            return "CONFLICT: Conflicting SKU record found with name '" + record.name + "' and SKU number '" \
                   + record.sku_number + "', in conflict with database entry with with name '" \
                   + list3[0].name + "' and SKU number '" \
                   + str(list3[0].sku_num) \
                   + "' at line '" + str(number_records_imported + 2) + "' in the SKU CSV file.", list3[0]
    if (file_prefix == "ingredients"):
        models_list = models.Ingredient.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record_converted.name and item.number == record_converted.number
                    and item.vendor_info == record_converted.vendor_info and
                    item.package_size == record_converted.package_size and item.cost == record_converted.cost
                    and item.comment == record_converted.comment):
                return "identical", None
            elif (item.name == record_converted.name and record_converted.number == -1
                    and item.vendor_info == record_converted.vendor_info and
                    item.package_size == record_converted.package_size and item.cost == record_converted.cost
                    and item.comment == record_converted.comment):
                return "identical", None
        list2 = models.Ingredient.objects.filter(name=record_converted.name)
        list3 = models.Ingredient.objects.filter(number=record_converted.number)
        if (len(list2) > 0):
            # TODO: Ask user for override.
            return "CONFLICT: Conflicting Ingredient record found with name '" + record.name \
                   + "' and number '" + record.number + "', in conflict with database entry with name '" \
                   + list2[0].name + "' and number '" \
                   + str(list2[0].number) + "' at line '" + str(number_records_imported + 2) \
                   + "' in the Ingredient CSV file.", list2[0]
        if (len(list3) > 0):
            # TODO: Ask user for override.
            return "CONFLICT: Conflicting Ingredient record found with name '" + record.name \
                   + "' and number '" + record.number + "', in conflict with database entry with name '" \
                   + list3[0].name + "' and number '" \
                   + str(list3[0].number) + "' at line '" + str(number_records_imported + 2) \
                   + "' in the Ingredient CSV file.", list3[[0]]
    if (file_prefix == "product_lines"):
        models_list = models.ProductLine.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record_converted.name):
                return "identical", None
        list2 = models.ProductLine.objects.filter(name=record_converted.name)
        if (len(list2) > 0):
            # TODO: Ask user for override.
            return "CONFLICT: Conflicting Product Line record found with name '" + list2[0].name \
                   + "' at line '" + str(number_records_imported + 2) \
                   + "' in the product_lines CSV file.", list2[0]
    if (file_prefix == "formulas"):
        models_list = models.IngredientQty.objects.filter(quantity=Decimal(record.quantity))
        for item in models_list:
            if (item.sku.sku_num == int(record.sku_number) and item.ingredient.number == int(record.ingredient_number)
                    and item.quantity == Decimal(record.quantity)):
                return "identical", None
        # Do we need to check or non-identical match here?
    return "", None


def check_for_match_name_or_id(new_record, record_list, file_prefix, num_records_imported):
    """
    Checks to see if a record being parsed has any conflicts with records already parsed.
    :param new_record: The record being parsed.
    :param record_list: List of records already parsed.
    :param file_prefix: The prefix to the file being imported.
    :param num_records_imported: The number of records parsed so far.
    :return: str indicating an error if there is one
    """
    row_num = 0
    for record in record_list:
        row_num += 1
        if (file_prefix == "skus"):
            if (new_record.sku_number == record.sku_number and new_record.sku_number != "-1"):
                return "ERROR: Duplicate SKU number(s) '" + new_record.sku_number + "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
            if (new_record.case_upc == record.case_upc):
                return "ERROR: Duplicate Case UPC number(s) '" + new_record.case_upc + "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
        if (file_prefix == "ingredients"):
            if (new_record.name == record.name):
                return "ERROR: Duplicate name '" + new_record.name + "' in Ingredients CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
            if (new_record.number == record.number and new_record.number != "-1"):
                return "ERROR: Duplicate Ingredient number '" + new_record.number + \
                       "' in Ingredients CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported) + "'"
        if (file_prefix == "product_lines"):
            if (new_record.name == record.name):
                return "ERROR: Duplicate name '" + new_record.name + "' in Product Lines CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
        if (file_prefix == "formulas"):
            if (new_record.sku_number == record.sku_number and
                    new_record.ingredient_number == record.ingredient_number):
                return "ERROR: Matching SKU/Ingredient pairing '" + new_record.sku + " / " + new_record.ingredient \
                       + "' in Formulas CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported + 2) + "'"
    return ""


def header_check(header, header_correct, file_prefix):
    """
    Checks if the header for a given file is correct.
    :param header: What the header actually is.
    :param header_correct: What the header should be.
    :param file_prefix: The prefix to the file being checked, used to determine if header #cols is correct.
    :return: True/False for success/failure, str to indicate the error
    """
    if file_prefix == "skus":
        if len(header) != 8:
            return False, "ERROR: Header is not correct in SKU CSV file. Too many or not enough columns."
    if file_prefix == "ingredients":
        if len(header) != 6:
            return False, "ERROR: Header is not correct in Ingredients CSV file. Too many or not enough columns."
    if file_prefix == "product_lines":
        if len(header) != 1:
            return False, "ERROR: Header is not correct in Product Lines CSV file. Too many or not enough columns."
    if file_prefix == "formulas":
        if len(header) != 3:
            return False, "ERROR: Header is not correct in Formulas CSV file. Too many or not enough columns."
    col = 0
    for item in header:
        # print(item)
        # try:
        #     print(unicodedata.name(item[0]))
        # except:
        #     print("unable to get unicode data")
        #if header_correct[col] != re.sub(r'[^a-zA-Z0-9_# ]', '', item):
        if header_correct[col] != item.replace(u'\ufeff', ''):
            headerError = "ERROR: csv header = '" + item + "' but should be '" + header_correct[col] + "'"
            return False, headerError
        col += 1
    return True, ""


def prefix_check(filename):
    """
    Checks if the prefix to the file is valid.
    :param filename: The full filename of the file being imported.
    :return: The correct prefix to the file if it exists, True/False to indicate success/failure
    """
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


def choose_product_line(csv_data_object, product_line_dict):
    valid_product_line_local = False
    valid_product_line_database = False
    chosen_product_line = None

    if csv_data_object.product_line in product_line_dict:
        valid_product_line_local = True
        chosen_product_line = product_line_dict[csv_data_object.product_line]

    temp_product_name_list = models.ProductLine.objects.filter(name=csv_data_object.product_line)
    if len(temp_product_name_list) > 0:
        valid_product_line_database = True
        chosen_product_line = temp_product_name_list[0]

    valid_product_line = valid_product_line_database or valid_product_line_local

    if not valid_product_line:
        return False, ("Import failed for SKU CSV file. \nERROR: Product Line name '" + csv_data_object.product_line
                + "' in SKU CSV file is not a valid name. It is not in the database "
                  "or in the product_lines CSV file attempting to be imported.")
    else:
        return True, chosen_product_line
