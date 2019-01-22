import sys
import csv
import CSVData

# test = "skus"
# test = "ingredients"
# test = "product_lines"
# test = "sku_ingredients"
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
        for filename in self.filenames:
            file_prefix, valid = prefix_check(filename)
            if(valid):
                data, num_records, success = parser(filename)
                if(success):
                    self.data_dict[file_prefix] = data
                    self.number_records_dict[file_prefix] = num_records
                else:
                    print("Parsing failed for: " + filename)
            else:
                print("Invalid file prefix for: " + filename)

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


def parser(filename):
    file_prefix, valid = prefix_check(filename)
    if not valid:
        print("FILE NAME INVALID: Terminating import...")
        return None, None, False

    header_correct = headerDict[file_prefix + ".csv"]
    parsed_data = []
    num_records_imported = 0

    with open(filename, 'r') as csvfile:
        data_reader = csv.reader(csvfile, quotechar='|')
        header_valid = True
        header_check_complete = False
        header_issue = ""
        for row in data_reader:
            if not header_check_complete:
                header_valid, header_issue = header_check(row, header_correct)
                header_check_complete = True
                continue
            if not header_valid:
                print("HEADER INVALID: Terminating import...")
                print(header_issue)
                return
            method_to_call = getattr(sys.modules[__name__], file_prefix + "_parser_helper")
            temp_data = method_to_call(row)
            if (check_for_identical_record(temp_data)):
                if (check_for_match_name_or_id):
                    parsed_data.append(temp_data)
                    num_records_imported += 1

    return parsed_data, num_records_imported, True


def skus_parser_helper(row):
    return CSVData.SKUData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def ingredients_parser_helper(row):
    return CSVData.IngredientData(row[0], row[1], row[2], row[3], row[4], row[5])


def product_lines_parser_helper(row):
    return CSVData.ProductLineData(row[0])


def sku_ingredients_parser_helper(row):
    return CSVData.SKUIngredientData(row[0], row[1], row[2])


def check_for_identical_record(record):
    # TODO: check database to see if COMPLETELY IDENTICAL record already exists here
    return True


def check_for_match_name_or_id():
    # TODO: Figure out what is supposed to be done here exactly and do it
    return True


def header_check(header, headerCorrect):
    col = 0
    for item in header:
        if headerCorrect[col] != item:
            headerError = "ERROR: header = '" + item + "' but should be '" + headerCorrect[col] + "'"
            return False, headerError
        col += 1
    return True, ""


def prefix_check(filename):
    file_prefix = ""
    valid = True
    for prefix in CSVData.validFilePrefixes:
        if filename.startswith(prefix):
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
