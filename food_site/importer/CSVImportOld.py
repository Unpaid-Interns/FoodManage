import csv
from sku_manage import models
from decimal import Decimal

headerDict = {
    "skus.csv": ["SKU#", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Ingr#", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formulas.csv": ["SKU#", "Ingr#", "Quantity"]
}

'''
    validFilePrefixes's contents can be changed but MUST remain in order of what was originally:
    skus, ingredients, product_lines, formulas
    with any additions being after those 4 (names of those 4 can be changed freely!
'''
validFilePrefixes = ["skus", "ingredients", "product_lines", "formulas"]

path_prefix = "importer/"


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
                data, conflict_data, num_to_import, num_ignored, num_conflict, file_read_successfully, error_message \
                    = read_file(filename, file_prefix, self.data_dict)
                # if successful, write all data to class returned from function
                if file_read_successfully:
                    self.total_num_records_imported += num_to_import
                    self.total_num_records_ignored += num_ignored
                    self.total_num_records_conflict += num_conflict
                    self.data_dict[file_prefix] = data
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

        if validFilePrefixes[2] in self.data_dict:
            models.ProductLine.objects.bulk_create(self.data_dict[validFilePrefixes[2]])
        if validFilePrefixes[0] in self.data_dict:
            models.SKU.objects.bulk_create(self.data_dict[validFilePrefixes[0]])
        if validFilePrefixes[1] in self.data_dict:
            models.Ingredient.objects.bulk_create(self.data_dict[validFilePrefixes[1]])
        if validFilePrefixes[3] in self.data_dict:
            models.IngredientQty.objects.bulk_create(self.data_dict[validFilePrefixes[3]])

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
                new_conflict_records_list.append([data.get_serializable_string_array(), message])
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
                if len(data_string_array) == len(headerDict[validFilePrefixes[0] + ".csv"]):
                    chosen_product_line = choose_product_line_for_sku(data_string_array[6], self.data_dict)
                    data = models.SKU(sku_num=int(data_string_array[0]), name=data_string_array[1],
                                      case_upc=Decimal(data_string_array[2]),
                                      unit_upc=Decimal(data_string_array[3]), unit_size=data_string_array[4],
                                      units_per_case=int(data_string_array[5]),
                                      product_line=chosen_product_line, comment=data_string_array[7])
                elif len(data_string_array) == len(headerDict[validFilePrefixes[1] + ".csv"]):
                    data = models.Ingredient(number=int(data_string_array[0]), name=data_string_array[1],
                                             vendor_info=data_string_array[2],
                                             package_size=data_string_array[3], cost=Decimal(data_string_array[4]),
                                             comment=data_string_array[5])
                elif len(data_string_array) == len(headerDict[validFilePrefixes[2] + ".csv"]):
                    data = models.ProductLine(name=data_string_array[0])
                elif len(data_string_array) == len(headerDict[validFilePrefixes[3] + ".csv"]):
                    _, _, chosen_sku, chosen_ingredient = choose_sku_and_ingredient_for_formula(
                        int(data_string_array[0]), int(data_string_array[2]), self.data_dict)
                    data = models.IngredientQty(chosen_sku, chosen_ingredient, Decimal(data_string_array[2]))
                if data is None:
                    return original_dict
                conflict_database_data = None
                if len(data_string_array) == len(headerDict[validFilePrefixes[0] + ".csv"]):
                    # TODO: Figure out a way that this won't create a conflict
                    case_upc_conflicts = models.SKU.objects.filter(case_upc=data.case_upc)
                    sku_num_conflicts = models.SKU.objects.filter(sku_num=data.sku_num)
                    if len(case_upc_conflicts) > 0:
                        conflict_database_data = case_upc_conflicts[0]
                    elif len(sku_num_conflicts) > 0:
                        conflict_database_data = sku_num_conflicts[0]
                elif len(data_string_array) == len(headerDict[validFilePrefixes[1] + ".csv"]):
                    # TODO: Figure out a way that this won't create a conflict
                    ingr_num_conflicts = models.Ingredient.objects.filter(number=data.number)
                    ingr_name_conflicts = models.Ingredient.objects.filter(name=data.name)
                    if len(ingr_name_conflicts) > 0:
                        conflict_database_data = ingr_name_conflicts[0]
                    elif len(ingr_num_conflicts) > 0:
                        conflict_database_data = ingr_num_conflicts[0]
                if conflict_database_data is None:
                    return original_dict
                new_conflict_records_list.append([data, conflict_database_data, message])
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
            for row in data_reader:
                has_rows = True
                if not header_check_complete:
                    header_valid, header_issue = header_check(row, header_correct, file_prefix)
                    header_check_complete = True
                    continue
                if not header_valid:
                    return None, None, None, None, None, False, \
                           "HEADER INVALID: Terminating import... \n" + header_issue

                # Call appropriate helper method
                temp_data = "ERROR: Parser methods failed. You should not see this error, please alert an admin."
                if file_prefix == validFilePrefixes[0]:
                    temp_data = skus_parser_helper(row, num_records_parsed, data_dict)
                elif file_prefix == validFilePrefixes[1]:
                    temp_data = ingredients_parser_helper(row, num_records_parsed)
                elif file_prefix == validFilePrefixes[2]:
                    temp_data = product_lines_parser_helper(row, num_records_parsed)
                elif file_prefix == validFilePrefixes[3]:
                    temp_data = formulas_parser_helper(row, num_records_parsed, data_dict)
                if isinstance(temp_data, str):
                    return None, None, None, None, None, False, temp_data

                # Check for matching database records
                matching_check = check_for_match_name_or_id(temp_data, parsed_data, file_prefix, num_records_parsed)
                if matching_check == "":
                    database_record_check, conflicting_database_model = check_for_identical_record(temp_data,
                                                                                                   file_prefix,
                                                                                                   num_records_parsed)
                    if database_record_check == "":
                        # parsed_data.append(temp_data, file_prefix)
                        parsed_data.append(temp_data)
                        num_records_parsed += 1
                    elif database_record_check == "identical":
                        num_records_parsed += 1
                        num_record_ignored += 1
                    elif "CONFLICT:" in database_record_check:
                        conflicting_records_tpl.append([temp_data, conflicting_database_model, database_record_check])
                        num_records_parsed += 1
                        num_record_conflicted += 1
                    else:
                        return None, None, None, None, None, False, database_record_check
                else:
                    return None, None, None, None, None, False, matching_check
            if not has_rows:
                return None, None, None, None, None, False, "ERROR: File is empty. Aborting import."
    except FileNotFoundError:
        return None, None, None, None, None, False, "*ERROR: File not found. Unable to open file: '" + filename + "'."
    # except:
    #     return None, None, None, None, None, False, "*ERROR: File type not valid or unknown error."
    return parsed_data, conflicting_records_tpl, num_records_parsed - num_record_ignored - num_record_conflicted, \
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
        if header_correct[col] != item.replace(u'\ufeff', ''):
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
    """

    pl_success, chosen_product_line_or_error_message = choose_product_line_for_sku(row[6], data_dict)
    if not pl_success:
        return chosen_product_line_or_error_message

    if len(row) != len(headerDict[validFilePrefixes[0] + ".csv"]):
        return ("ERROR: Problem with number of entries in SKU CSV file at row #" + str(num_records_parsed + 2) +
                ", needs 8 entries but has " + str(len(row)) + " entries.")
    if row[0] == "":
        row[0] = "-1"
    else:
        if not integer_check(row[0]):
            return "ERROR: SKU# in SKU CSV file is not an integer in row #" + str(num_records_parsed + 2) \
                   + "and col #1."
    for i in range(1, 7):
        if row[i] == "":
            return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                    + str(i + 1) + ". Entry in this row/column is required but is blank.")
        if i in [2, 3]:
            if not decimal_check(row[i]):
                return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                        + str(i + 1) + ". Entry in this row/column is required to be a decimal value but is not.")
            if i == 2:
                try:
                    models.validate_upc(Decimal(row[i]))
                except:
                    return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                            + str(i + 1) + ". case_upc in this row/col is invalid/does not conform to standards.")
            if i == 3:
                try:
                    models.validate_upc(Decimal(row[i]))
                except:
                    return ("ERROR: Problem in SKU CSV file in row #" + str(num_records_parsed + 2) + " and col #"
                            + str(i + 1) + ". unit_upc in this row/col is invalid/does not conform to standards.")
        if i in [5]:
            if not integer_check(row[i]):
                return ("ERROR: Problem with 'Count per case' in SKU CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a integer value "
                                                      "but is not.")
    return models.SKU(sku_num=int(row[0]), name=row[1], case_upc=Decimal(row[2]),
                      unit_upc=Decimal(row[3]), unit_size=row[4],
                      units_per_case=int(row[5]), product_line=chosen_product_line_or_error_message,
                      comment=row[7])


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


def ingredients_parser_helper(row, num_records_parsed):
    """
    Helper function for ingredient.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != len(headerDict[validFilePrefixes[1] + ".csv"]):
        return ("ERROR: Problem with number of entries in Ingredients CSV file at row #" + str(
            num_records_parsed + 2) +
                ", needs 6 entries but has " + str(len(row)) + " entries.")
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
        if i in [4]:
            if not decimal_check(row[i]):
                return ("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a decimal value "
                                                      "but is not.")
            if Decimal(row[i]) < 0:
                return ("ERROR: Problem with 'Cost' in Ingredient CSV file in row #" + str(num_records_parsed + 2)
                        + " and col #" + str(i + 1) + ". Entry in this row/column is required to be a positive value "
                                                      "but is not.")
    return models.Ingredient(number=int(row[0]), name=row[1], vendor_info=row[2],
                             package_size=row[3], cost=Decimal(row[4]), comment=row[5])


def product_lines_parser_helper(row, num_records_parsed):
    """
    Helper function for product_lines.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """
    if len(row) != len(headerDict[validFilePrefixes[2] + ".csv"]):
        return ("ERROR: Problem with number of entries in Product Lines CSV file at row #" + str(
            num_records_parsed + 2) + ", needs 1 entries but has " + str(len(row)) + " entries.")
    return models.ProductLine(name=row[0])


def formulas_parser_helper(row, num_records_parsed, data_dict):
    """
    Helper function for formulas.csv file
    :param row: The row being parsed
    :param num_records_parsed: The number of records parsed so far - used for determining current row in file
    :return: str for error if there is one, otherwise return the data
    """

    if len(row) != len(headerDict[validFilePrefixes[3] + ".csv"]):
        return ("ERROR: Problem with number of entries in Formulas CSV file at row #"
                + str(num_records_parsed + 2) + ", needs 3 entries but has " + str(len(row)) + " entries.")
    for i in [0, 1, 2]:
        if i in [0, 1]:
            if not integer_check(row[i]):
                return "ERROR: Problem in Formulas CSV file in row #" + str(num_records_parsed + 2) + " and col #" \
                       + str(i + 1) + ". Entry in this column must be an integer value but is not."
        if i in [2]:
            if not decimal_check(row[i]):
                return "ERROR: Problem in Formulas CSV file with 'Quantity' in row #" + str(num_records_parsed + 2) \
                       + " and col #" \
                       + str(i + 1) + ". Entry in this column must be an decimal value but is not."

    chosen_successfully, error_message, chosen_sku, chosen_ing = \
        choose_sku_and_ingredient_for_formula(int(row[0]), int(row[1]), data_dict)

    if not chosen_successfully:
        return error_message
    else:
        return models.IngredientQty(sku=chosen_sku, ingredient=chosen_ing,
                                    quantity=Decimal(row[2]))


def choose_sku_and_ingredient_for_formula(sku_num, ing_number, data_dict):
    chosen_sku = None
    chosen_ingredient = None

    # check if sku_number for i is in database
    sku_number_in_database = False
    temp_sku_list = models.SKU.objects.filter(sku_num=sku_num)
    if len(temp_sku_list) > 0:
        sku_number_in_database = True
        chosen_sku = temp_sku_list[0]

    # check if sku_number for i is in to-be-imported stuff
    sku_number_in_local = False
    if validFilePrefixes[0] in data_dict:
        for sku in data_dict[validFilePrefixes[0]]:
            if sku.sku_num == sku_num:
                sku_number_in_local = True
                chosen_sku = sku

    sku_number_valid = sku_number_in_local or sku_number_in_database

    if not sku_number_valid:
        return False, "Import failed for formulas CSV file. \nERROR: SKU Number '" + str(sku_num) \
               + "' in formulas CSV file is invalid. It does not " \
                 "exist in either the database or the SKU CSV being imported.", None, None

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
                 "exist in either the database or the Ingredient CSV being imported.", None, None

    return True, "", chosen_sku, chosen_ingredient


def decimal_check(number_string):
    """
    Checks if a string can be converted to a decimal
    :param number_string: str input to be checked as a decimal
    :return: True/False to indicate if it is/is not a decimal
    """
    try:
        _ = Decimal(number_string)
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
                chosen_num = skus_num_list[len(skus_num_list) - 1] + 1
                skus_num_list.append(chosen_num)
                skus_num_list.sort()
            s.sku_num = chosen_num


def fill_in_ingr_nums(data_dict):
    ingredients_that_need_numbers = []
    ingr_nums_list = []
    if validFilePrefixes[0] in data_dict:
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
                chosen_num = ingr_nums_list[len(ingr_nums_list) - 1] + 1
                ingr_nums_list.append(chosen_num)
                ingr_nums_list.sort()
            i.number = chosen_num


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
            if new_record.sku.sku_num == record.sku.sku_num and \
                    new_record.ingredient.number == record.ingredient.number:
                return "ERROR: Matching SKU/Ingredient pairing '" + str(new_record.sku.sku_num) \
                       + " / " + str(new_record.ingredient.number) \
                       + "' in Formulas CSV file at lines '" + str(row_num) + "' and '" \
                       + str(num_records_imported + 2) + "'"
    return ""


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
    if file_prefix == validFilePrefixes[0]:
        models_list = models.SKU.objects.filter(name=record.name)
        for item in models_list:
            if (item.name == record.name and item.sku_num == record.sku_num and
                    item.case_upc == record.case_upc and item.unit_upc == record.unit_upc
                    and item.unit_size == record.unit_size and item.units_per_case ==
                    record.units_per_case and item.product_line.name == record.product_line.name and
                    item.comment == record.comment):
                return "identical", None
            elif (item.name == record.name and record.sku_num == -1 and
                  item.case_upc == record.case_upc and item.unit_upc == record.unit_upc
                  and item.unit_size == record.unit_size and item.units_per_case ==
                  record.units_per_case and item.product_line.name == record.product_line.name and
                  item.comment == record.comment):
                return "identical", None
        list2 = models.SKU.objects.filter(case_upc=record.case_upc)
        list3 = models.SKU.objects.filter(sku_num=record.sku_num)
        if len(list2) > 0:
            return "CONFLICT: Conflicting SKU record found with name '" + record.name + "' and Case UPC '" \
                   + str(record.case_upc) \
                   + "', in conflict with database entry with name '" \
                   + list2[0].name + "' and Case UPC '" \
                   + str(list2[0].case_upc) + \
                   "' at line '" + \
                   str(number_records_imported + 2) + "' in the SKU CSV file.", list2[0]
        if len(list3) > 0:
            return "CONFLICT: Conflicting SKU record found with name '" + record.name + "' and SKU number '" \
                   + str(record.sku_number) + "', in conflict with database entry with with name '" \
                   + list3[0].name + "' and SKU number '" \
                   + str(list3[0].sku_num) \
                   + "' at line '" + str(number_records_imported + 2) + "' in the SKU CSV file.", list3[0]
    if file_prefix == validFilePrefixes[1]:
        models_list = models.Ingredient.objects.filter(name=record.name)
        for item in models_list:
            print(item.name, record.name)
            print(item.number, record.number)
            print(item.vendor_info, record.vendor_info)
            print(item.package_size, record.package_size)
            print(Decimal(item.cost), Decimal(record.cost))
            print(item.comment, record.comment)
            if (item.name == record.name and item.number == record.number
                    and item.vendor_info == record.vendor_info and
                    item.package_size == record.package_size and item.cost == record.cost
                    and item.comment == record.comment):
                return "identical", None
            elif (item.name == record.name and record.number == -1
                  and item.vendor_info == record.vendor_info and
                  item.package_size == record.package_size and item.cost == record.cost
                  and item.comment == record.comment):
                return "identical", None
        list2 = models.Ingredient.objects.filter(name=record.name)
        list3 = models.Ingredient.objects.filter(number=record.number)
        if len(list2) > 0:
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
        models_list = models.IngredientQty.objects.filter(quantity=record.quantity)
        for item in models_list:
            if (item.sku.sku_num == record.sku.sku_num and item.ingredient.number == record.ingredient.number
                    and item.quantity == record.quantity):
                return "identical", None
        # Do we need to check or non-identical match here?
        models.IngredientQty.objects.filter(sku__sku_num=record.sku.sku_num).delete()
    return "", None


def sort_filename_array(filename_array):
    new_filename_array = []
    for i in [2, 0, 1, 3]:
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
