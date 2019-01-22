import CSVImport
import CSVExport
import CSVData

# test = "import"
test = "export"

if __name__ == '__main__':
    if test == "import":
        print("CLASS TEST STARTING...")
        importer = CSVImport.CSVImport()
        filenames = ["skus.csv", "ingredients.csv", "product_lines.csv", "sku_ingredients.csv"]
        importer.set_filenames(filenames)
        importer.parse()

        # Print out parsed results
        try:
            for file_prefix in importer.data_dict:
                print("Data for: " + file_prefix + ".csv")
                print("Number of records imported = ", importer.number_records_dict[file_prefix])
                for item in importer.data_dict[file_prefix]:
                    print(item)
                print("")
        except UnicodeError:
            print("error printing data")
    elif test == "export":
        exporter = CSVExport.CSVExport()

        # skus.csv export
        data = []
        # number, name, case upc, unit upc, unit size, count per case, product line name, comment
        print("SKUS EXPORT TEST STARTING...")
        item1 = CSVData.SKUData(str(1), "First Name", str(1), str(1), str(1), str(3), "Product Line 1",
                                "First comment")
        item2 = CSVData.SKUData(str(2), "Second Name", str(1), str(9), str(1), str(3), "Product Line 2",
                                "Second comment")
        item3 = CSVData.SKUData(str(3), "Third Name", str(1), str(1), str(2), str(3), "Product Line 3",
                                "Third comment")
        item4 = CSVData.SKUData(str(4), "Fourth Name", str(7), str(1), str(1), str(3), "Product Line 4",
                                "Fourth comment")
        data.append(item1)
        data.append(item2)
        data.append(item3)
        data.append(item4)
        exporter.export_to_csv(data)

        # ingredients.csv export
        data = []
        # number, name, vendor_info, package_size, cost, comment
        print("INGREDIENTS EXPORT TEST STARTING...")
        item1 = CSVData.IngredientData(str(1), "First Name", "Vendor Info 1", str(1), str(143), "First comment")
        item2 = CSVData.IngredientData(str(2), "Second Name", "Vendor Info 2", str(9), str(1234), "Second comment")
        item3 = CSVData.IngredientData(str(3), "Third Name", "Vendor Info 3", str(1), str(234), "Third comment")
        item4 = CSVData.IngredientData(str(4), "Fourth Name", "Vendor Info 4", str(1), str(33), "Fourth comment")
        data.append(item1)
        data.append(item2)
        data.append(item3)
        data.append(item4)
        exporter.export_to_csv(data)

        # product_lines.csv export
        data = []
        # name
        print("PRODUCT LINES EXPORT TEST STARTING...")
        item1 = CSVData.ProductLineData("Product 1")
        item2 = CSVData.ProductLineData("Product 2")
        item3 = CSVData.ProductLineData("Product 3")
        item4 = CSVData.ProductLineData("Product 4")
        data.append(item1)
        data.append(item2)
        data.append(item3)
        data.append(item4)
        exporter.export_to_csv(data)

        # sku_ingredients.csv export
        data = []
        # sku number, ingredient number, quantity
        print("SKU INGREDIENTS EXPORT TEST STARTING...")
        item1 = CSVData.SKUIngredientData(str(1), str(11), str(80085))
        item2 = CSVData.SKUIngredientData(str(2), str(22), str(8008135))
        item3 = CSVData.SKUIngredientData(str(3), str(33), str(5812))
        item4 = CSVData.SKUIngredientData(str(4), str(44), str(17))
        data.append(item1)
        data.append(item2)
        data.append(item3)
        data.append(item4)
        exporter.export_to_csv(data)
