import sys
import csv
import csv_data

test = "skus"
# test = "ingredients"
# test = "product_lines"
# test = "sku_ingredients" # NOT YET IMPLEMENTED

headerDict = {
    "skus.csv": ["Number", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Number", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "sku_ingredients.csv": ["SKU Number", "Ingredient Number", "Quantity"]
}


def parser(filename):
    headerCorrect = headerDict[filename]
    parsed_data = []

    with open(filename, 'r') as csvfile:
        dataReader = csv.reader(csvfile, quotechar='|')
        headerValid = True
        checkComplete = False
        headerIssue = ""
        for row in dataReader:
            if not checkComplete:
                headerValid, headerIssue = headerCheck(row, headerCorrect)
                checkComplete = True
                continue
            if not headerValid:
                print("HEADER INVALID")
                print(headerIssue)
                return
            method_to_call = getattr(sys.modules[__name__], filename.split(".")[0] + "_parser_helper")
            parsed_data.append(method_to_call(row))

    return parsed_data


def skus_parser_helper(row):
    return csv_data.SKUData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def ingredients_parser_helper(row):
    return csv_data.IngredientData(row[0], row[1], row[2], row[3], row[4], row[5])


def product_lines_parser_helper(row):
    return csv_data.ProductLineData(row[0])

def sku_ingredients_parser_helper(row):
    return csv_data.SKUIngredientData(row[0])


def headerCheck(header, headerCorrect):
    col = 0
    headerValid = True
    for item in header:
        if headerCorrect[col] != item:
            headerError = "ERROR: header = '" + item + "' but should be '" + headerCorrect[col] + "'"
            headerValid = False
            return headerValid, headerError
        col += 1
    return headerValid, ""


if __name__ == '__main__':
    data = parser(test + ".csv")
    try:
        for item in data:
            print(item)
    except:
        print("error printing data")
