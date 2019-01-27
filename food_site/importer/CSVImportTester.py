from importer import CSVImport

test = "import"


def run():
    if test == "import":
        print("")
        print("CSVImportTester: STARTING TEST...")
        importer = CSVImport.CSVImport()
        filenames = ["importer/product_lines.csv", "importer/ingredients.csv", \
                     "importer/skus.csv", "importer/formula.csv"]
        importer.set_filenames(filenames)
        success, result_message = importer.parse()
        print(result_message)
        print("")

        # Print out parsed results
        # try:
        #     for file_prefix in importer.data_dict:
        #         print("Data for: " + file_prefix + ".csv")
        #         print("Number of records imported = ", importer.number_records_dict[file_prefix])
        #         for item in importer.data_dict[file_prefix]:
        #             print(item)
        #         print("")
        # except UnicodeError:
        #     print("error printing data")


if __name__ == '__main__':
    run()
