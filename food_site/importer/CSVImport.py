import csv
from sku_manage import models
import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from itertools import chain

headerDict = {
    "skus.csv": ["SKU#", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "PL Name",
                 "Formula#", "Formula factor", "ML Shortnames", "Rate", "Mfg setup cost", "Mfg run cost", "Comment"],
    "ingredients.csv": ["Ingr#", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formulas.csv": ["Formula#", "Name", "Ingr#", "Quantity", "Comment"]
}

'''
    validFilePrefixes's contents can be changed but MUST remain in order of what was originally:
    skus, ingredients, product_lines, formulas
    with any additions being after those 4 (names of those 4 can be changed freely!
'''
validFilePrefixes = ["skus", "ingredients", "product_lines", "formulas"]

validUnits = ['ounce', 'oz', 'pound', 'lb', 'ton', 'gram', 'g',
              'kilogram', 'kg', 'fluidounce', 'floz', 'pint', 'pt',
              'quart', 'qt', 'gallon', 'gal', 'milliliter', 'ml',
              'liter', 'l', 'ct', 'count']

unit_mappings = {
    "ounce": "Ounce",
    "oz": "Ounce",
    "pound": "Pound",
    "lb": "Pound",
    "ton": "Ton",
    "gram": "Gram",
    "g": "Gram",
    "kilogram": "Kilogram",
    "kg": "Kilogram",
    "fluidounce": "Fluid Ounce",
    "floz": "Fluid Ounce",
    "pint": "Pint",
    "pt": "Pint",
    "quart": "Quart",
    "qt": "Quart",
    "gallon": "Gallon",
    "gal": "Gallon",
    "milliliter": "Milliliter",
    "ml": "Milliliter",
    "liter": "Liter",
    "l": "Liter",
    "ct": "Count",
    "count": "Count"
}

path_prefix = "importer/"
path_prefix2 = "importer/import_test_suite/"


class CSVImport:
    def __init__(self, filename_array=[]):
        self.filename_array = filename_array
        self.total_num_records_imported = 0
        self.total_num_records_ignored = 0
        self.total_num_records_conflict = 0
        self.data_dict = dict()
        self.conflict_dict = dict()

    def import_csv(self):
        """
        Parses the data
        :return: bool for success/failure, bool for conflicts, error str
        """
        # Ensure the order of import is correct by sorting files
        self.filename_array = sort_filename_array(self.filename_array)

        # loop through all files to be import
        for filename in self.filename_array:
            # validate file prefix
            file_prefix, valid_prefix = prefix_check(filename)
            # if prefix valid, proceed with import
            if valid_prefix:
                # read the file and check for conflicts
                data, sku_mfg_line_data, formulas_data, conflict_data, num_to_import, num_ignored, num_conflict, file_read_successfully, error_message \
                    = read_file(filename, file_prefix, self.data_dict)
                # if successful, write all data to class returned from function
                if file_read_successfully:
                    self.total_num_records_imported += num_to_import
                    self.total_num_records_ignored += num_ignored
                    self.total_num_records_conflict += num_conflict
                    self.data_dict[file_prefix] = data
                    if len(formulas_data) > 0:
                        self.data_dict["formulas_extra"] = formulas_data
                    if len(sku_mfg_line_data) > 0:
                        self.data_dict["ML"] = sku_mfg_line_data
                    # if there are conflicts, make sure to add them to the dictionary
                    if len(conflict_data) > 0:
                        self.conflict_dict[file_prefix] = conflict_data
                    commit_success_message, commit_successful = self.commit_to_database()
                    # if conflict dictionary empty, return success
                    if not self.conflict_dict:
                        if commit_successful:
                            return True, False, "Import completed successfully with #" + str(
                                self.total_num_records_imported) \
                                   + " records imported and #" + str(self.total_num_records_ignored) \
                                   + " records ignored and #" + str(
                                self.total_num_records_conflict) + " records in conflict."

                        else:
                            return False, False, commit_success_message
                    # if conflicts exist, return failure with message to specify there are conflict
                    else:
                        if commit_successful:
                            return True, True, "Import completed with #" + str(self.total_num_records_imported) \
                                   + " records imported and #" + str(self.total_num_records_ignored) \
                                   + " records ignored and #" + str(self.total_num_records_conflict) \
                                   + " records in conflict. \n" + \
                                   "Conflicts exist. Please confirm how to handle them below."
                        else:
                            return False, False, commit_success_message
                # if NOT successful, return error
                else:
                    return False, False, "Import failed for: " + filename + ". \n" + error_message
            # if prefix NOT valid, return error
            else:
                return False, False, "Import failed for: " + filename + ". \n" + "ERROR: file name " + filename \
                       + " is invalid, must begin with valid prefix 'skus', \
                        'ingredients', 'product_lines', or 'formulas'"

    def commit_to_database(self):
        """
        Commits data to database
        :return: error str (blank string if no error)
        """

        fill_in_sku_nums(self.data_dict)
        fill_in_ingr_nums(self.data_dict)
        fill_in_formula_nums(self.data_dict)

        try:
            clean_data(self.data_dict)
        except ValidationError as error_message:
            return "ERROR: Database error = " + str(error_message), False

        if validFilePrefixes[1] in self.data_dict:
            models.Ingredient.objects.bulk_create(self.data_dict[validFilePrefixes[1]])
        if validFilePrefixes[2] in self.data_dict:
            models.ProductLine.objects.bulk_create(self.data_dict[validFilePrefixes[2]])
        if validFilePrefixes[3] in self.data_dict:
            if "formulas_extra" in self.data_dict:
                models.Formula.objects.bulk_create(self.data_dict["formulas_extra"])
                fix_ingredient_qty(self.data_dict)
            models.IngredientQty.objects.bulk_create(self.data_dict[validFilePrefixes[3]])
        if validFilePrefixes[0] in self.data_dict:
            models.SKU.objects.bulk_create(self.data_dict[validFilePrefixes[0]])
            if "ML" in self.data_dict:
                fix_sku_mfg_lines(self.data_dict)
                models.SkuMfgLine.objects.bulk_create(self.data_dict["ML"])

        return "", True

    def add_filename(self, filename):
        self.filename_array.append(filename)

    def remove_filename(self, filename_to_remove):
        temp_filename_array = []
        for filename in self.filename_array:
            if filename != filename_to_remove:
                temp_filename_array.append(filename)
        self.filename_array = temp_filename_array

    def clear_filenames(self):
        self.filename_array = []

    def set_filenames(self, filename_array):
        self.filename_array = filename_array

    def make_serializable_conflict_dict(self, conflict_dict_temp):
        if conflict_dict_temp is None:
            conflict_dict_temp = self.conflict_dict
        serializable_dict = dict()
        for file_prefix in conflict_dict_temp:
            new_conflict_records_list = []
            conflict_records_list = conflict_dict_temp[file_prefix]
            for conflict_tuple in conflict_records_list:
                data = conflict_tuple[0]
                message = conflict_tuple[2]
                shortnames_array = conflict_tuple[3]
                new_conflict_records_list.append([data.get_serializable_string_array(), message, shortnames_array])
            serializable_dict[file_prefix] = new_conflict_records_list
        return serializable_dict

    def get_conflict_dict_from_serializable(self, serializable_dict):
        # print("START OF GET SERIALZABLE")
        original_dict = dict()
        for file_prefix in serializable_dict:
            # print(file_prefix + " in GET SERIALZABLE")
            new_conflict_records_list = []
            conflict_records_list = serializable_dict[file_prefix]
            for conflict_tuple in conflict_records_list:
                data_string_array = conflict_tuple[0]
                # print(len(data_string_array))
                message = conflict_tuple[1]
                shortnames_array = conflict_tuple[2]
                data = None
                if len(data_string_array) + 1 == len(headerDict[validFilePrefixes[0] + ".csv"]):
                    # print("HELLO FROM GET SERIAZABLE")
                    _, chosen_product_line = choose_product_line_for_sku(data_string_array[6], self.data_dict)
                    _, chosen_formula = choose_formula_for_sku(int(data_string_array[7]), self.data_dict)
                    data = models.SKU(sku_num=int(data_string_array[0]), name=data_string_array[1],
                                      case_upc=data_string_array[2], unit_upc=data_string_array[3],
                                      unit_size=data_string_array[4], units_per_case=int(data_string_array[5]),
                                      product_line=chosen_product_line,
                                      formula=chosen_formula, formula_scale=float(data_string_array[8]),
                                      mfg_rate=float(data_string_array[9]),
                                      mfg_setup_cost=Decimal(data_string_array[10]),
                                      mfg_run_cost=Decimal(data_string_array[11]),
                                      comment=data_string_array[12])
                elif len(data_string_array) - 1 == len(headerDict[validFilePrefixes[1] + ".csv"]):
                    data = models.Ingredient(number=int(data_string_array[0]), name=data_string_array[1],
                                             vendor_info=data_string_array[2],
                                             package_size=float(data_string_array[3]),
                                             package_size_units=data_string_array[4],
                                             cost=Decimal(data_string_array[5]),
                                             comment=data_string_array[6])
                elif len(data_string_array) == len(headerDict[validFilePrefixes[2] + ".csv"]):
                    data = models.ProductLine(name=data_string_array[0])
                elif len(data_string_array) == len(headerDict[validFilePrefixes[3] + ".csv"]):
                    _, _, chosen_ingredient = choose_ingredient_for_formula(int(data_string_array[1]), self.data_dict)
                    _, chosen_ingredient = get_formula_if_exists_for_formula(int(data_string_array[0]), self.data_dict,
                                                                             None, False)
                    data = models.IngredientQty(formula=chosen_ingredient, ingredient=chosen_ingredient,
                                                quantity=float(data_string_array[2]),
                                                quantity_units=data_string_array[3])
                if data is None:
                    # print("RETURNING EARLY 1")
                    return original_dict
                conflict_database_data = None
                if len(data_string_array) + 1 == len(headerDict[validFilePrefixes[0] + ".csv"]):
                    case_upc_conflicts = models.SKU.objects.filter(case_upc=data.case_upc)
                    sku_num_conflicts = models.SKU.objects.filter(sku_num=data.sku_num)
                    if len(case_upc_conflicts) > 0:
                        conflict_database_data = case_upc_conflicts[0]
                    elif len(sku_num_conflicts) > 0:
                        conflict_database_data = sku_num_conflicts[0]
                elif len(data_string_array) - 1 == len(headerDict[validFilePrefixes[1] + ".csv"]):
                    ingr_num_conflicts = models.Ingredient.objects.filter(number=data.number)
                    ingr_name_conflicts = models.Ingredient.objects.filter(name=data.name)
                    if len(ingr_name_conflicts) > 0:
                        conflict_database_data = ingr_name_conflicts[0]
                    elif len(ingr_num_conflicts) > 0:
                        conflict_database_data = ingr_num_conflicts[0]
                if conflict_database_data is None:
                    # print("RETURNING EARLY 2")
                    return original_dict
                new_conflict_records_list.append([data, conflict_database_data, message, shortnames_array])
            # print(new_conflict_records_list)
            original_dict[file_prefix] = new_conflict_records_list
        return original_dict


def read_file(filename, file_prefix, data_dict):
    """
        Parses the given file
        :param filename: str of file's name
        :param file_prefix: the prefix of the file
        :param data_dict: all data parsed so far but not yet imported
        :return: parsed data, number records imported, bool indicating success, and error message string
        """

    # Initialize variables
    header_correct = headerDict[file_prefix + ".csv"]
    parsed_data = []
    sku_mfg_lines_data = []
    formulas_data = []
    conflicting_records_tpl = []
    num_records_parsed = 0
    num_record_ignored = 0
    num_record_conflicted = 0

    try:
        # Open the csv file, read only
        with open(filename, 'r', encoding='utf-8') as csvfile:
            data_reader = csv.reader(csvfile, quotechar='"')
            header_valid = True
            header_check_complete = False
            header_issue = ""
            has_rows = False
            used_formulas_neg_numbers_list = [-1]
            for row in data_reader:
                sku_mfg_lines_array = []
                shortname_array = []
                has_rows = True
                if not header_check_complete:
                    header_valid, header_issue = header_check(row, header_correct, file_prefix)
                    header_check_complete = True
                    continue
                if not header_valid:
                    return None, None, None, None, None, None, None, False, \
                           "HEADER INVALID: Terminating import... \n" + header_issue

                # Call appropriate helper method
                temp_data = "ERROR: Parser methods failed. You should not see this error, please alert an admin."
                if file_prefix == validFilePrefixes[0]:
                    temp_data, sku_mfg_lines_array, shortname_array = skus_parser_helper(row, num_records_parsed,
                                                                                         data_dict)
                elif file_prefix == validFilePrefixes[1]:
                    temp_data = ingredients_parser_helper(row, num_records_parsed)
                elif file_prefix == validFilePrefixes[2]:
                    temp_data = product_lines_parser_helper(row, num_records_parsed)
                elif file_prefix == validFilePrefixes[3]:
                    temp_data, formula, used_formulas_neg_numbers_list = \
                        formulas_parser_helper(row, num_records_parsed, data_dict, formulas_data,
                                               used_formulas_neg_numbers_list)
                if isinstance(temp_data, str):
                    return None, None, None, None, None, None, None, False, temp_data

                # Check for matching database records
                matching_check = check_for_match_name_or_id(temp_data, parsed_data, file_prefix,
                                                            num_records_parsed)
                if matching_check == "":
                    database_record_check, conflicting_database_model = check_for_identical_record(temp_data,
                                                                                                   shortname_array,
                                                                                                   file_prefix,
                                                                                                   num_records_parsed)
                    if database_record_check == "":
                        # parsed_data.append(temp_data, file_prefix)
                        parsed_data.append(temp_data)
                        if file_prefix == validFilePrefixes[0]:
                            sku_mfg_lines_data = sku_mfg_lines_data + sku_mfg_lines_array
                        if file_prefix == validFilePrefixes[3]:
                            if formula is not None:
                                formulas_data.append(formula)
                        num_records_parsed += 1
                    elif database_record_check == "identical":
                        num_records_parsed += 1
                        num_record_ignored += 1
                    elif "CONFLICT:" in database_record_check:
                        conflicting_records_tpl.append([temp_data, conflicting_database_model, database_record_check,
                                                        shortname_array])
                        num_records_parsed += 1
                        num_record_conflicted += 1
                    else:
                        return None, None, None, None, None, None, None, False, database_record_check
                else:
                    return None, None, None, None, None, None, None, False, matching_check
            if not has_rows:
                return None, None, None, None, None, None, None, False, "ERROR: File is empty. Aborting import."
    except FileNotFoundError:
        return None, None, None, None, None, None, None, False, "*ERROR: File not found. Unable to open file: '" + filename + "'."
    except:
        return None, None, None, None, None, None, None, False, "*ERROR: File type not valid or unknown error."
    return parsed_data, sku_mfg_lines_data, formulas_data, conflicting_records_tpl, \
           num_records_parsed - num_record_ignored - num_record_conflicted, \
           num_record_ignored, num_record_conflicted, True, ""


def prefix_check(filename):
    """
    Checks if the prefix to the file is valid.
    :param filename: The full filename of the file being imported.
    :return: The correct prefix to the file if it exists, True/False to indicate success/failure
    """
    filename_no_importer_prefix = filename
    if filename.startswith(path_prefix):
        filename_no_importer_prefix = filename[len(path_prefix):]
    if filename.startswith(path_prefix2):
        filename_no_importer_prefix = filename[len(path_prefix2):]
    file_prefix = ""
    valid = True
    for prefix in validFilePrefixes:
        if filename_no_importer_prefix.startswith(prefix):
            file_prefix = prefix
    if file_prefix == "":
        valid = False
    return file_prefix, valid


def header_check(header, header_correct, file_prefix):
    """
    Checks if the header for a given file is correct.
    :param header: What the header actually is.
    :param header_correct: What the header should be.
    :param file_prefix: The prefix to the file being checked, used to determine if header #cols is correct.
    :return: True/False for success/failure, str to indicate the error
    """
    if file_prefix == validFilePrefixes[0]:
        if len(header) < len(headerDict[validFilePrefixes[0] + ".csv"]):
            return False, "ERROR: Header is not correct in SKU CSV file. Not enough columns."
        if len(header) > len(headerDict[validFilePrefixes[0] + ".csv"]):
            return False, "ERROR: Header is not correct in SKU CSV file. Too many columns."
    if file_prefix == validFilePrefixes[1]:
        if len(header) < len(headerDict[validFilePrefixes[1] + ".csv"]):
            return False, "ERROR: Header is not correct in Ingredients CSV file. Not enough columns."
        if len(header) > len(headerDict[validFilePrefixes[1] + ".csv"]):
            return False, "ERROR: Header is not correct in Ingredients CSV file. Too many columns."
    if file_prefix == validFilePrefixes[2]:
        if len(header) < len(headerDict[validFilePrefixes[2] + ".csv"]):
            return False, "ERROR: Header is not correct in Product Lines CSV file. Not enough columns."
        if len(header) > len(headerDict[validFilePrefixes[2] + ".csv"]):
            return False, "ERROR: Header is not correct in Product Lines CSV file. Too many columns."
    if file_prefix == validFilePrefixes[3]:
        if len(header) < len(headerDict[validFilePrefixes[3] + ".csv"]):
            return False, "ERROR: Header is not correct in Formulas CSV file. Not enough columns."
        if len(header) > len(headerDict[validFilePrefixes[3] + ".csv"]):
            return False, "ERROR: Header is not correct in Formulas CSV file. Too many columns."
    col = 0
    for item in header:
        # ensure that Excel added character \ufeff is removed
        if header_correct[col].lower() != item.replace(u'\ufeff', '').lower():
            headerError = "ERROR: csv header = '" + item + "' but should be '" + header_correct[col] + "'"
            return False, headerError
        col += 1
    return True, ""


def skus_parser_helper(row, num_records_parsed, data_dict):
    """
    Helper function for skus.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :param data_dict: Dictionary of data parsed so far, indexed by file prefix
    :return: str for error if there is one, otherwise return the data
    :return: sku/manufacturing line array
    """
    # Header: ["SKU#", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "PL Name",
    #           0       1       2           3           4               5               6
    #                  "Formula#", "Formula factor", "ML Shortnames", "Rate", "Mfg setup cost", "Mfg run cost",
    #                   7              8                9               10      11                  12
    #                  "Comment"]
    #                   13
    shortname_array = []

    if len(row) != len(headerDict[validFilePrefixes[0] + ".csv"]):
        return ("ERROR: Problem with number of entries in SKU CSV file at row #" + str(num_records_parsed + 2) +
                ", needs " + str(len(headerDict[validFilePrefixes[0] + ".csv"])) +
                " entries but has " + str(len(row)) + " entries."), None, shortname_array
    if row[0] == "":
        row[0] = "-1"
    else:
        if not integer_check(row[0]):
            return ("ERROR: SKU# in SKU CSV file is not an integer in row #" + str(num_records_parsed + 2) \
                    + "and col #1."), None, shortname_array
    for i in chain(range(1, 9), range(10, 13)):
        if row[i] == "":
            if i == 8:
                row[i] = "1"
            else:
                return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry in this row/column is required but is blank."), None, shortname_array
        if i == 1:
            if len(row[i]) > 32:
                return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry '" + str(row[i]) + "' in this row/column is greater than 32 characters."
                        ), None, shortname_array
        if i in [2, 3, 8, 10]:
            if not float_check(row[i]):
                return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry '" + str(row[i]) + "' in this row/column is required to be a "
                                                                   "decimal value but is not."), None, shortname_array
            if i == 2:
                try:
                    models.validate_upc(row[i])
                except ValidationError as error_message:
                    return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                            + str(i + 1) + ". case_upc '" + str(
                                row[i]) + "' in this row/col is invalid/does not conform"
                                          " to standards. " + error_message.message + "."), None, shortname_array
            if i == 3:
                try:
                    models.validate_upc(row[i])
                except ValidationError as error_message:
                    return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                            + str(i + 1) + ". unit_upc'" + str(row[i]) + "' in this row/col is invalid/does not conform"
                                                                         " to standards. " + error_message.message +
                            "."), None, shortname_array
        if i in [4]:
            if len(row[i]) > 256:
                return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry in this row/column is greater than the 256 character limit."), None,\
                        shortname_array
        if i in [5]:
            if not integer_check(row[i]):
                return ("ERROR: Problem with 'Count per case' in SKU CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry '" + str(row[i]) + "' in this row/column is required "
                                                                               "to be a integer value but is not."), None, shortname_array
        if i in [10, 11]:
            usd_check, usd_value = usd_valid_check(row[i])
            if not usd_check:
                return("ERROR: ?")
            if not decimal_check(usd_value):
                return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry '" + str(row[i]) + "' in this row/column is required to be a "
                                                                   "decimal value but is not."), None, shortname_array
            row[i] = str(round(Decimal(usd_value), 2))
    pl_success, chosen_product_line_or_error_message = choose_product_line_for_sku(row[6], data_dict)
    if not pl_success:
        return chosen_product_line_or_error_message, None, shortname_array

    formula_success, chosen_formula_or_error_message = choose_formula_for_sku(int(row[7]), data_dict)
    if not formula_success:
        return chosen_formula_or_error_message, None, shortname_array

    sku = models.SKU(sku_num=int(row[0]), name=row[1], case_upc=row[2], unit_upc=row[3],
                     unit_size=row[4], units_per_case=int(row[5]), product_line=chosen_product_line_or_error_message,
                     formula=chosen_formula_or_error_message, formula_scale=float(row[8]), mfg_rate=float(row[10]),
                     mfg_setup_cost=Decimal(row[11]), mfg_run_cost=Decimal(row[12]), comment=row[13])

    mfg_line_array = []
    for ml_shortname in row[9].split(','):
        if ml_shortname == "":
            continue
        shortname_array.append(ml_shortname)
        for line in mfg_line_array:
            if line.mfg_line.shortname == ml_shortname:
                return ("ERROR: Problem with 'ML Shortnames' in SKU CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(
                            i + 1) + ". Entry '" + ml_shortname + "' in the list of shortnames appears "
                                                                  "multiple times in file."), None, \
                       shortname_array
        ml_success, chosen_mfg_line = make_sku_mfg_line(ml_shortname, sku)
        if not ml_success:
            return ("ERROR: Problem with 'ML Shortnames' in SKU CSV file in row #" + str(num_records_parsed + 2)
                    + " and col #" + str(i + 1) + ". Entry '" + ml_shortname + "' in the list of shortnames does "
                                                                               "not exist in the database."), None, \
                   shortname_array
        else:
            mfg_line_array.append(chosen_mfg_line)
    return sku, mfg_line_array, shortname_array


def choose_product_line_for_sku(product_line_string, data_dict):
    product_line_dict = make_product_lines_dict(data_dict)

    valid_product_line_local = False
    valid_product_line_database = False
    chosen_product_line = None

    if product_line_string in product_line_dict:
        valid_product_line_local = True
        chosen_product_line = product_line_dict[product_line_string]

    temp_product_name_list = models.ProductLine.objects.filter(name=product_line_string)
    if len(temp_product_name_list) > 0:
        valid_product_line_database = True
        chosen_product_line = temp_product_name_list[0]

    valid_product_line = valid_product_line_database or valid_product_line_local

    if not valid_product_line:
        return False, ("Import failed for SKU CSV file. \nERROR: Product Line name '" + product_line_string
                       + "' in SKU CSV file is not a valid name. It is not in the database "
                         "or in the product_lines CSV file attempting to be imported.")
    else:
        return True, chosen_product_line


def choose_formula_for_sku(formula_number, data_dict):
    chosen_formula = None

    if formula_number == -1:
        return False, None

    formula_list = models.Formula.objects.filter(number=formula_number)
    if len(formula_list) > 0:
        chosen_formula = formula_list[0]

    if "formulas_extra" in data_dict:
        for formula in data_dict["formulas_extra"]:
            if formula.number == formula_number:
                chosen_formula = formula

    if chosen_formula is not None:
        return True, chosen_formula
    else:
        return False, ("ERROR: Formula number '" + str(formula_number)
                       + "' in SKU CSV file is not a valid formula. It is not in the database "
                         "or in a formulas CSV file attempting to be imported.")


def make_sku_mfg_line(ml_shortname, sku):
    # Do I need to check here if something exists in database?
    mfg_line_list = models.ManufacturingLine.objects.filter(shortname=ml_shortname)
    if len(mfg_line_list) > 0:
        mfg_line = mfg_line_list[0]
    else:
        return False, None
    return True, models.SkuMfgLine(sku=sku, mfg_line=mfg_line)


def fix_sku_mfg_lines(data_dict):
    if "ML" in data_dict:
        for sku_mfg_line in data_dict["ML"]:
            skus_list = models.SKU.objects.filter(sku_num=sku_mfg_line.sku.sku_num)
            if len(skus_list) > 0:
                sku_mfg_line.sku = skus_list[0]


def ingredients_parser_helper(row, num_records_parsed):
    """
    Helper function for ingredient.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    # Header:  [    "Ingr#",    "Name",     "Vendor Info",  "Size",     "Cost",     "Comment"]
    # Header#: [        0           1               2           3           4           5
    if len(row) != len(headerDict[validFilePrefixes[1] + ".csv"]):
        return ("ERROR: Problem with number of entries in Ingredients CSV file at row #" + str(
            num_records_parsed + 2) +
                ", needs " + str(len(headerDict[validFilePrefixes[1] + ".csv"])) + " entries but has " + str(
                    len(row)) + " entries.")
    if row[0] == "":
        row[0] = "-1"
    else:
        if not integer_check(row[0]):
            return "ERROR: Ingr# in Ingredient CSV file is not an integer in row #" \
                   + str(num_records_parsed + 2) + "and col #1."
    for i in [1, 3, 4]:
        if row[i] == "":
            return ("ERROR: Problem in Ingredient CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                    + str(i + 1) + ". Entry in this row/column is required but is blank.")
        if i == 1:
            if len(row[i]) > 256:
                return ("ERROR: Problem in Formulas CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry '" + str(
                            row[i]) + "' in this row/column is greater than 256 characters."
                        ), None, None
        if i == 3:
            number_string, unit_string, matches_regex, size_success = get_number_and_unit(row[i])
            if not matches_regex:
                return ("ERROR: Problem with 'Size' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column does not conform to required "
                                                      "package size standard.")
            if not size_success:
                error_string = "ERROR: Problem with 'Size' in Ingredient CSV file in row #" \
                               + str(num_records_parsed + 2) + " and col #" + str(i + 1) + ". "
                if number_string is None and unit_string is None:
                    error_addition = "number and unit"
                elif number_string is None:
                    error_addition = "number"
                elif unit_string is None:
                    error_addition = "unit"
                error_string = error_string + "Entry in this row/column has an invalid " + error_addition + " in the " \
                               + "number/unit pair."
                return error_string
        if i in [4]:
            usd_check, usd_value = usd_valid_check(row[i])
            if not usd_check:
                return ("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column does not conform to USD formatting"
                                                      "standards.")
            if not float_check(usd_value):
                return ("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a decimal value "
                                                      "but is not.")
            if float(usd_value) < 0:
                return ("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a non-zero "
                                                      "value but is not.")
            row[i] = str(round(Decimal(usd_value), 2))
            if Decimal(row[i]) > 9999999999.99:
                return ("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column is required to be 12 digits or less "
                                                      "value but is " + str(len(row[i])) + " digits.")
    return models.Ingredient(number=int(row[0]), name=row[1], vendor_info=row[2],
                             package_size=float(number_string), package_size_units=unit_string,
                             cost=Decimal(row[4]), comment=row[5])


def product_lines_parser_helper(row, num_records_parsed):
    """
    Helper function for product_lines.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != len(headerDict[validFilePrefixes[2] + ".csv"]):
        return ("ERROR: Problem with number of entries in Product Lines CSV file at row #" + str(
            num_records_parsed + 2) + ", needs " + str(len(headerDict[validFilePrefixes[2] + ".csv"]))
                + " entries but has " + str(len(row)) + " entries.")
    if len(row[0]) > 256:
        return ("ERROR: Problem in 'Product Line' at row #" + str(num_records_parsed + 2) + ". Name entry is greater"
                                                                                            "than 256 characters.")
    return models.ProductLine(name=row[0])


def formulas_parser_helper(row, num_records_parsed, data_dict, formula_local_data, used_neg_numbers_list):
    """
    Helper function for formulas.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :param data_dict: dictionary of data parsed so far
    :return: str for error if there is one, None; otherwise return IngredientQty and Formula (none if already imported)
    """
    # Header: ["Formula#", "Name", "Ingr#", "Quantity", "Comment"]
    #            0           1       2           3           4

    if len(row) != len(headerDict[validFilePrefixes[3] + ".csv"]):
        return ("ERROR: Problem with number of entries in Formulas CSV file at row #"
                + str(num_records_parsed + 2) + ", needs " + str(len(headerDict[validFilePrefixes[3] + ".csv"]))
                + " entries but has " + str(len(row)) + " entries."), None, None
    for i in [0, 1, 2, 3]:
        if i == 0:
            if row[i] == "":
                row[0] = str(used_neg_numbers_list[len(used_neg_numbers_list) - 1] - 1)
                used_neg_numbers_list.append(int(row[0]))
        if i in [1]:
            if row[i] == "":
                return ("ERROR: Problem in Formulas CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry in this row/column is required but is blank."), None, None
            if len(row[i]) > 32:
                return ("ERROR: Problem in Formulas CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry '" + str(
                            row[i]) + "' in this row/column is greater than 32 characters."
                        ), None, None
        if i in [0, 2]:
            if not integer_check(row[i]):
                return "ERROR: Problem in Formulas CSV file in row #" + str(num_records_parsed + 2) + " and col #" \
                       + str(i + 1) + ". Entry in this column must be an integer value but is not.", None, None
        if i in [3]:
            number_string, unit_string, matches_regex, size_success = get_number_and_unit(row[i])
            if not matches_regex:
                return ("ERROR: Problem with 'Size' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column does not conform to required "
                                                      "package size standard."), None, None
            if not size_success:
                error_string = "ERROR: Problem with 'Size' in Ingredient CSV file in row #" \
                               + str(num_records_parsed + 2) + " and col #" + str(i + 1) + ". "
                if number_string is None and unit_string is None:
                    error_addition = "number and unit"
                elif number_string is None:
                    error_addition = "number"
                elif unit_string is None:
                    error_addition = "unit"
                error_string = error_string + "Entry in this row/column has an invalid " + error_addition + " in the " \
                               + "number/unit pair."
                return error_string, None, None

    ing_chosen_successfully, error_message, chosen_ing = \
        choose_ingredient_for_formula(int(row[2]), data_dict)
    if not ing_chosen_successfully:
        return error_message, None, None

    formula_chosen_successfully, chosen_formula, formula_error_message = get_formula_if_exists_for_formula(int(row[0]),
                                                                                                           row[1],
                                                                                                           data_dict,
                                                                                                           formula_local_data,
                                                                                                           True)
    if formula_error_message != "":
        return formula_error_message, None, None
    if not formula_chosen_successfully:
        chosen_formula = models.Formula(name=row[1], number=int(row[0]), comment=row[4])
        ing_qty_model = models.IngredientQty(formula=chosen_formula, ingredient=chosen_ing,
                                             quantity=float(number_string), quantity_units=unit_string)
        try:
            ing_qty_model.clean()
            return ing_qty_model, chosen_formula, used_neg_numbers_list
        except ValidationError as error_message:
            return ("ERROR: Problem in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                    + ". " + str(error_message).replace("[", "").replace("'", "").replace("]", "") + "."), None, None
    else:
        ing_qty_model = models.IngredientQty(formula=chosen_formula, ingredient=chosen_ing,
                                             quantity=float(number_string), quantity_units=unit_string)
        try:
            ing_qty_model.clean()
            return ing_qty_model, None, used_neg_numbers_list
        except ValidationError as error_message:
            return ("ERROR: Problem in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                    + ". " + str(error_message).replace("[", "").replace("'", "").replace("]", "") + "."), None, None


def get_formula_if_exists_for_formula(formula_number, formula_name, data_dict, formula_local_data, check_local):
    chosen_formula = None
    formula_number_in_database = False
    formula_number_in_local = False

    # check if formula_number for i is in database
    temp_formula_list = models.Formula.objects.filter(number=formula_number)
    if len(temp_formula_list) > 0:
        if temp_formula_list[0].name != formula_name:
            return False, None, ("ERROR: Formula number being imported with number '" + str(
                formula_number) + "' with name '"
                                 + formula_name + "' in violation with database formula with number '"
                                 + str(temp_formula_list[0].number) + "' and name '"
                                 + temp_formula_list[0].name + "'.")
        formula_number_in_database = True
        chosen_formula = temp_formula_list[0]

    if check_local:
        # check if formula_number for i is in to-be-imported stuff
        if "formulas_extra" in data_dict:
            for formula in data_dict["formulas_extra"]:
                if formula.number == formula_number:
                    if formula.name != formula_name:
                        return False, None, ("ERROR: Formula number being imported with number '" + str(
                            formula_number) + "' with name '"
                                             + formula_name + "' in violation with database formula with number '"
                                             + str(formula.number) + "' and name '" + formula.name + "'.")
                    formula_number_in_local = True
                    chosen_formula = formula
        if len(formula_local_data) > 0:
            for formula in formula_local_data:
                if formula.number == formula_number:
                    if formula.name != formula_name:
                        return False, None, ("ERROR: Formula number being imported with number '" + str(
                            formula_number) + "' with name '"
                                             + formula_name + "' in violation with database formula with number '"
                                             + str(formula.number) + "' and name '" + formula.name + "'.")
                    formula_number_in_local = True
                    chosen_formula = formula

    formula_number_valid = formula_number_in_database or formula_number_in_local

    if not formula_number_valid:
        return False, None, ""

    return True, chosen_formula, ""


def choose_ingredient_for_formula(ing_number, data_dict):
    chosen_ingredient = None

    # check if ingredient_number for i is in database
    ingredient_number_in_database = False
    temp_ingredient_list = models.Ingredient.objects.filter(number=ing_number)
    if len(temp_ingredient_list) > 0:
        ingredient_number_in_database = True
        chosen_ingredient = temp_ingredient_list[0]

    # check if ingredient_number for i is in to-be-imported stuff
    ingredient_number_in_local = False
    if validFilePrefixes[1] in data_dict:
        for ing in data_dict[validFilePrefixes[1]]:
            if ing.number == ing_number:
                ingredient_number_in_local = True
                chosen_ingredient = ing

    ingredient_number_valid = ingredient_number_in_database or ingredient_number_in_local

    if not ingredient_number_valid:
        return False, "Import failed for formulas CSV file. \nERROR: Ingredient Number '" + str(ing_number) \
               + "' in formulas CSV file is invalid. It does not " \
                 "exist in either the database or the Ingredient CSV being imported.", None

    return True, "", chosen_ingredient


def float_check(number_string):
    """
    Checks if a string can be converted to a float
    :param number_string: str input to be checked as a float
    :return: True/False to indicate if it is/is not a float
    """
    try:
        _ = float(number_string)
        return True
    except:
        return False


def integer_check(number_string):
    """
    Checks if a string can be converted to an integer
    :param number_string: str input to be checked as an integer
    :return: True/False to indicate if it is/is not an integer
    """
    try:
        _ = int(number_string)
        return True
    except:
        return False


def decimal_check(number_string):
    """
    Checks if a string can be converted to an integer
    :param number_string: str input to be checked as an integer
    :return: True/False to indicate if it is/is not an integer
    """
    try:
        _ = Decimal(number_string)
        return True
    except:
        return False


def make_product_lines_dict(data_dict):
    product_line_dict = dict()
    if validFilePrefixes[2] in data_dict:
        for i in data_dict[validFilePrefixes[2]]:
            product_line_dict[i.name] = i.convert_to_database_model()
    return product_line_dict


def fill_in_sku_nums(data_dict):
    skus_that_need_numbers = []
    skus_num_list = []
    if validFilePrefixes[0] in data_dict:
        for i in data_dict[validFilePrefixes[0]]:
            if i.sku_num != -1:
                skus_num_list.append(i.sku_num)
            else:
                skus_that_need_numbers.append(i)
        for s in models.SKU.objects.all():
            skus_num_list.append(s.sku_num)
        skus_num_list.sort()
        for s in skus_that_need_numbers:
            chosen_num = -1
            for index in range(0, len(skus_num_list) - 1):
                if chosen_num != -1:
                    continue
                if skus_num_list[index] + 1 != skus_num_list[index + 1]:
                    chosen_num = skus_num_list[index] + 1
                    skus_num_list.append(chosen_num)
                    skus_num_list.sort()
            if chosen_num == -1:
                if len(skus_num_list) > 0:
                    chosen_num = skus_num_list[len(skus_num_list) - 1] + 1
                else:
                    chosen_num = 1
                skus_num_list.append(chosen_num)
                skus_num_list.sort()
            s.sku_num = chosen_num


def fill_in_ingr_nums(data_dict):
    ingredients_that_need_numbers = []
    ingr_nums_list = []
    if validFilePrefixes[1] in data_dict:
        for i in data_dict[validFilePrefixes[1]]:
            if i.number != -1:
                ingr_nums_list.append(i.number)
            else:
                ingredients_that_need_numbers.append(i)
        for i in models.Ingredient.objects.all():
            ingr_nums_list.append(i.number)
        ingr_nums_list.sort()
        for i in ingredients_that_need_numbers:
            chosen_num = -1
            for index in range(0, len(ingr_nums_list)):
                if chosen_num != -1:
                    continue
                if ingr_nums_list[index] + 1 != ingr_nums_list[index + 1]:
                    chosen_num = ingr_nums_list[index] + 1
                    ingr_nums_list.append(chosen_num)
                    ingr_nums_list.sort()
            if chosen_num == -1:
                if len(ingr_nums_list) > 0:
                    chosen_num = ingr_nums_list[len(ingr_nums_list) - 1] + 1
                else:
                    chosen_num = 1
                ingr_nums_list.append(chosen_num)
                ingr_nums_list.sort()
            i.number = chosen_num


def fill_in_formula_nums(data_dict):
    formulas_that_need_numbers = []
    formulas_nums_list = []
    if "formulas_extra" in data_dict:
        for f in data_dict["formulas_extra"]:
            if f.number >= 0:
                formulas_nums_list.append(f.number)
            else:
                formulas_that_need_numbers.append(f)
        for f in models.Formula.objects.all():
            formulas_nums_list.append(f.number)
        formulas_nums_list.sort()
        for f in formulas_that_need_numbers:
            chosen_num = -1
            for index in range(0, len(formulas_nums_list) - 1):
                if chosen_num != -1:
                    continue
                if formulas_nums_list[index] + 1 != formulas_nums_list[index + 1]:
                    chosen_num = formulas_nums_list[index + 1] + 1
                    formulas_nums_list.append(chosen_num)
                    formulas_nums_list.sort()
            if chosen_num == -1:
                if len(formulas_nums_list) > 0:
                    chosen_num = formulas_nums_list[len(formulas_nums_list) - 1] + 1
                else:
                    chosen_num = 1
                formulas_nums_list.append(chosen_num)
                formulas_nums_list.sort()
            f.number = chosen_num
        if validFilePrefixes[3] in data_dict:
            ing_qty_list = data_dict[validFilePrefixes[3]]
            for ing_qty in ing_qty_list:
                if ing_qty.formula.name == f.name:
                    ing_qty.formula = f


def check_for_match_name_or_id(new_record, record_list, file_prefix, num_records_imported):
    """
    Checks to see if a record being parsed has any conflicts with records already parsed.
    :param new_record: The record being parsed.
    :param record_list: List of records already parsed.
    :param file_prefix: The prefix to the file being imported.
    :param num_records_imported: The number of records parsed so far.
    :return: str indicating an error if there is one
    """
    row_num = 1
    for record in record_list:
        row_num += 1
        if file_prefix == validFilePrefixes[0]:
            if new_record.sku_num == record.sku_num and new_record.sku_num != -1:
                return "ERROR: Duplicate SKU number(s) '" + str(new_record.sku_num) + "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
            if new_record.case_upc == record.case_upc:
                return "ERROR: Duplicate Case UPC number(s) '" + str(new_record.case_upc) + \
                       "' in SKU CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
        if file_prefix == validFilePrefixes[1]:
            if new_record.name == record.name:
                return "ERROR: Duplicate name '" + new_record.name + "' in Ingredients CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
            if new_record.number == record.number and new_record.number != -1:
                return "ERROR: Duplicate Ingredient number '" + str(new_record.number) + \
                       "' in Ingredients CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported) + "'"
        if file_prefix == validFilePrefixes[2]:
            if new_record.name == record.name:
                return "ERROR: Duplicate name '" + new_record.name + "' in Product Lines CSV file at lines '" \
                       + str(row_num) + "' and '" + str(num_records_imported + 2) + "'"
        if file_prefix == validFilePrefixes[3]:
            if (record.formula.number == new_record.formula.number and record.formula.name == new_record.formula.name
                    and record.ingredient.number == new_record.ingredient.number):
                if record.quantity == new_record.quantity and record.quantity_units == new_record.quantity_units:
                    return ("ERROR: Duplicate formula entry with number '" + str(new_record.formula.number)
                            + "', name '" + new_record.formula.name + "' at lines '" + str(num_records_imported + 2)
                            + "' and '" + str(row_num) + '.')
                else:
                    return ("ERROR: Formula to be imported with number '" + str(new_record.formula.number) + "', name '"
                            + new_record.formula.name + "', and ingredient number '" + str(new_record.ingredient.number)
                            + "', and quantity '" + str(new_record.quantity) + new_record.quantity_units
                            + "' at line '" + str(num_records_imported + 2)
                            + "' conflicts with similar formula in file with same fields except with quantity '"
                            + str(record.quantity) + record.quantity_units + "' at line '" + str(row_num) + "'.")
    return ""


def check_for_identical_record(record, shortname_array, file_prefix, number_records_imported):
    """
    Checks for identical and/or conflicting records in the database
    :param record: The record being parsed
    :param file_prefix: The prefix to the file being imported
    :param number_records_imported: The number of records imported so far
    :return: str with the error if there is one
    """
    # Returns blank string if no identical record found
    # Could use filter to check for same name and ID but not other fields
    if file_prefix == validFilePrefixes[0]:
        models_list = models.SKU.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record.name and item.sku_num == record.sku_num and
                    item.case_upc == record.case_upc and item.unit_upc == record.unit_upc
                    and item.unit_size == record.unit_size and item.units_per_case ==
                    record.units_per_case and item.product_line.name == record.product_line.name and
                    item.formula.number == record.formula.number and item.formula_scale == record.formula_scale and
                    item.mfg_rate == record.mfg_rate and item.mfg_setup_cost == record.mfg_setup_cost and
                    item.mfg_run_cost == record.mfg_run_cost and item.comment == record.comment):
                sku_mfg_pass, sku_mfg_conflict_message = sku_mfg_line_check(record, shortname_array, item,
                                                                            number_records_imported)
                # print(sku_mfg_pass)
                # print(sku_mfg_conflict_message)
                if sku_mfg_pass:
                    return "identical", None
                else:
                    return sku_mfg_conflict_message, item
            elif (item.name == record.name and record.sku_num == -1 and
                  item.case_upc == record.case_upc and item.unit_upc == record.unit_upc
                  and item.unit_size == record.unit_size and item.units_per_case ==
                  record.units_per_case and item.product_line.name == record.product_line.name and
                  item.formula.number == record.formula.number and item.formula_scale == record.formula_scale and
                  item.mfg_rate == record.mfg_rate and item.mfg_setup_cost == record.mfg_setup_cost and
                  item.mfg_run_cost == record.mfg_run_cost and item.comment == record.comment):
                sku_mfg_pass, sku_mfg_conflict_message = sku_mfg_line_check(record, shortname_array, item,
                                                                            number_records_imported)
                if sku_mfg_pass:
                    return "identical", None
                else:
                    return sku_mfg_conflict_message, item
        list2 = models.SKU.objects.filter(case_upc=record.case_upc)
        list3 = models.SKU.objects.filter(sku_num=record.sku_num)
        if len(list2) > 0:
            if len(list3) > 0:
                if list2[0].sku_num != list3[0].sku_num:
                    return "ERROR: Conflict with multiple records in database. Record to be imported with " \
                           "number '" + str(record.sku_num) + "' and case_upc '" + str(record.case_upc) + "' at line '" \
                           + str(number_records_imported + 2) + "' in the SKU CSV file is conflict with " \
                                                                "database record with number '" + str(
                        list2[0].sku_num) + "' and case_upc '" \
                           + str(list2[0].case_upc) + \
                           "' and database record with number '" + str(list3[0].sku_num) + "' and case_upc '" \
                           + str(list3[0].case_upc) + "'.", None
            return "CONFLICT: Conflicting SKU record found with name '" + record.name + "' and Case UPC '" \
                   + str(record.case_upc) \
                   + "', in conflict with database entry with name '" \
                   + list2[0].name + "' and Case UPC '" \
                   + str(list2[0].case_upc) + \
                   "' at line '" + \
                   str(number_records_imported + 2) + "' in the SKU CSV file.", list2[0]
        if len(list3) > 0:
            return "CONFLICT: Conflicting SKU record found with name '" + record.name + "' and SKU number '" \
                   + str(record.sku_num) + "', in conflict with database entry with with name '" \
                   + list3[0].name + "' and SKU number '" \
                   + str(list3[0].sku_num) \
                   + "' at line '" + str(number_records_imported + 2) + "' in the SKU CSV file.", list3[0]
    if file_prefix == validFilePrefixes[1]:
        models_list = models.Ingredient.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record.name and item.number == record.number
                    and item.vendor_info == record.vendor_info and
                    item.package_size == record.package_size and item.cost == record.cost and
                    item.package_size_units == record.package_size_units
                    and item.comment == record.comment):
                return "identical", None
            elif (item.name == record.name and record.number == -1
                  and item.vendor_info == record.vendor_info and
                  item.package_size == record.package_size and item.cost == record.cost and
                  item.package_size_units == record.package_size_units
                  and item.comment == record.comment):
                return "identical", None
        list2 = models.Ingredient.objects.filter(name=record.name)
        list3 = models.Ingredient.objects.filter(number=record.number)
        if len(list2) > 0:
            if len(list3) > 0:
                if list2[0].name != list3[0].name:
                    return "ERROR: Conflict with multiple records in database. Record to be imported with " \
                           "name '" + record.name + "' and number '" + str(record.number) + "' at line '" \
                           + str(number_records_imported + 2) + "' in the Ingredient CSV file is conflict with " \
                                                                "database record with name '" + list2[
                               0].name + "' and number '" + str(list2[0].number) + \
                           "' and database record with name '" + list3[0].name + "' and number '" \
                           + str(list3[0].number) + "'.", None
            return "CONFLICT: Conflicting Ingredient record found with name '" + record.name \
                   + "' and number '" + str(record.number) + "', in conflict with database entry with name '" \
                   + list2[0].name + "' and number '" \
                   + str(list2[0].number) + "' at line '" + str(number_records_imported + 2) \
                   + "' in the Ingredient CSV file.", list2[0]
        if len(list3) > 0:
            return "CONFLICT: Conflicting Ingredient record found with name '" + record.name \
                   + "' and number '" + str(record.number) + "', in conflict with database entry with name '" \
                   + list3[0].name + "' and number '" \
                   + str(list3[0].number) + "' at line '" + str(number_records_imported + 2) \
                   + "' in the Ingredient CSV file.", list3[0]
    if file_prefix == validFilePrefixes[2]:
        models_list = models.ProductLine.objects.filter(name=record.name)
        for item in models_list:
            if item.name == record.name:
                return "identical", None
    if file_prefix == validFilePrefixes[3]:
        models_list = models.IngredientQty.objects.filter(formula__name=record.formula.name)
        for item in models_list:
            if (item.formula.number == record.formula.number and item.formula.name == record.formula.name
                    and item.ingredient.number == record.ingredient.number
                    and item.quantity == record.quantity and item.quantity_units == record.quantity_units):
                return "identical", None
            if (record.formula.number < 0 and item.formula.name == record.formula.name
                    and item.ingredient.number == record.ingredient.number
                    and item.quantity == record.quantity and item.quantity_units == record.quantity_units):
                return "identical", None
            if (item.formula.number == record.formula.number and item.formula.name == record.formula.name
                and item.ingredient.number == record.ingredient.number) and \
                    (item.quantity != record.quantity or item.quantity_units != record.quantity_units):
                return ("ERROR: Formula to be imported with number '" + str(record.formula.number) + "', name '"
                        + record.formula.name + "', and ingredient number '" + str(record.ingredient.number)
                        + "', and quantity '" + str(record.quantity) + record.quantity_units
                        + "' at line '" + str(number_records_imported + 2)
                        + "' conflicts with similar formula in database with same fields except with quantity '"
                        + str(item.quantity) + item.quantity_units + "'."), None
        models.IngredientQty.objects.filter(formula__number=record.formula.number).delete()
    return "", None


def sku_mfg_line_check(import_record, local_shortname_array, database_record, number_records_imported):
    sku_mfg_database_list = models.SkuMfgLine.objects.filter(sku__sku_num=import_record.sku_num)
    shortname_database_array = []
    for sku_mfg_line in sku_mfg_database_list:
        shortname_database_array.append(sku_mfg_line.mfg_line.shortname)
    for local_shortname in local_shortname_array:
        if local_shortname not in shortname_database_array:
            return False, ("CONFLICT: Conflicting SKU record found with name '" + import_record.name
                           + "' and Case UPC '"
                           + str(import_record.case_upc)
                           + "', in conflict with database entry with name '"
                           + database_record.name + "' and Case UPC '"
                           + str(database_record.case_upc) +
                           "' at line '" +
                           str(
                               number_records_imported + 2) + "' in the SKU CSV file. List of shortnames does not match. "
                                                              "Shortname '" + local_shortname + "' in SKU being imported "
                                                                                                "is not part of the SKU in the database.")
    for shortname_db in shortname_database_array:
        if shortname_db not in local_shortname_array:
            return False, (
                    "CONFLICT: Conflicting SKU record found with name '" + import_record.name + "' and Case UPC '"
                    + str(import_record.case_upc)
                    + "', in conflict with database entry with name '"
                    + database_record.name + "' and Case UPC '"
                    + str(database_record.case_upc) +
                    "' at line '" +
                    str(number_records_imported + 2) + "' in the SKU CSV file. List of shortnames does not match. "
                                                       "Shortname '" + shortname_db + "' in the database "
                                                                                      "is not part of the SKU being imported.")
    return True, ""


def sort_filename_array(filename_array):
    new_filename_array = []
    for i in [1, 2, 3, 0]:
        valid, filename = sort_filename_helper(filename_array, validFilePrefixes[i])
        if valid:
            new_filename_array.append(filename)
    if len(new_filename_array) == len(filename_array):
        return new_filename_array
    else:
        return filename_array


def sort_filename_helper(filename_array, prefix_to_search_for):
    for filename in filename_array:
        if prefix_to_search_for in filename:
            return True, filename
    return False, ""


def get_number_and_unit(mixed_unit):
    """
        Checks for identical and/or conflicting records in the database
        :param mixed_unit: string of the mixed unit (number and unit)
        :return: number string, unit string, boolean for matching regex, boolean for success
        """
    matches_regex, number_string, unit_string = mixed_unit_valid_check(mixed_unit)
    if matches_regex:
        if not float_check(number_string):
            # print("Not float: ", number_string, unit_string)
            return None, unit_string, matches_regex, False
        # strip unit of spaces, '.', make lowercase, and removes trailing 's'
        unit_string = unit_string.strip().replace('.', '').replace(' ', '').lower()
        if unit_string.endswith('s'):
            unit_string = unit_string[:-1]
        if unit_string in validUnits:
            # get proper string for database entry
            unit_string = unit_mappings[unit_string]
            return number_string, unit_string, matches_regex, True
        else:
            # print("unit_string NOT in validUnits: ", unit_string)
            return number_string, None, matches_regex, False
    else:
        # print("Doesn't match: ", number_string, unit_string)
        return None, None, matches_regex, False


def mixed_unit_valid_check(mixed_unit):
    pattern = re.compile("^(\d*\.?\d+)\s*(\D.*|)$")
    match = pattern.fullmatch(mixed_unit)
    if match is not None:
        return True, match.group(1), match.group(2)
    else:
        return False, None, None


def usd_valid_check(usd_expression):
    pattern = re.compile("^\s*\$?\s*([+-]?\d*\.?\d+)\D*$")
    match = pattern.fullmatch(usd_expression)
    if match is not None:
        return True, match.group(1)
    else:
        return False, None


def clean_data(data_dict):
    for key in data_dict:
        for item in data_dict[key]:
            item.full_clean()


def fix_ingredient_qty(data_dict):
    for item in data_dict[validFilePrefixes[3]]:
        formula_chosen_successfully, chosen_formula, error_message = get_formula_if_exists_for_formula(
            item.formula.number,
            item.formula.name, data_dict,
            None, False)
        if formula_chosen_successfully:
            item.formula = chosen_formula
