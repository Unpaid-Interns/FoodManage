from importer import CSVImport

test = "import"


def run():
    if test == "import":
        print("")
        print("CSVImportTester: STARTING TEST...")
        importer = CSVImport.CSVImport()
        # filenames = ["importer/product_lines2.csv", "importer/ingredients2.csv", \
        #              "importer/skus2.csv", "importer/formula2.csv"]
        filenames = ["importer/product_lines1.csv", "importer/ingredients1.csv",
                     "importer/skus1.csv", "importer/formula1.csv"]
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
