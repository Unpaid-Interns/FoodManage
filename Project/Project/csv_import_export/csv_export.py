import sys
import csv
import csv_data
import csv_import

test = "skus"


# test = "ingredients"
# test = "product_lines"
# test = "sku_ingredients"  # NOT YET IMPLEMENTED


def export_csv(data):
    with open('testExport.csv', 'w') as csvfile:
        dataWriter = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        dataWriter.writerow(csv_import.headerDict[test + ".csv"])
        for item in data:
            # print(item.exportData)
            dataWriter.writerow(item.exportData)


if __name__ == '__main__':
    data = []
    if (test == "skus"):
        item1 = csv_data.SKUData(str(1), "First Name", str(1), str(1), str(1), str(3), "Product Line 1",
                                 "First comment")
        item2 = csv_data.SKUData(str(2), "Second Name", str(1), str(9), str(1), str(3), "Product Line 2",
                                 "Second comment")
        item3 = csv_data.SKUData(str(3), "Third Name", str(1), str(1), str(2), str(3), "Product Line 3",
                                 "Third comment")
        item4 = csv_data.SKUData(str(4), "Fourth Name", str(7), str(1), str(1), str(3), "Product Line 4",
                                 "Fourth comment")
        data.append(item1)
        data.append(item2)
        data.append(item3)
        data.append(item4)
    elif (test == "ingredients"):
        # number, name, vendor_info, package_size, cost, comment
        item1 = csv_data.IngredientData(str(1), "First Name", "Vendor Info 1", str(1), str(143), "First comment")
        item2 = csv_data.IngredientData(str(2), "Second Name", "Vendor Info 2", str(9), str(1234), "Second comment")
        item3 = csv_data.IngredientData(str(3), "Third Name", "Vendor Info 3", str(1), str(234), "Third comment")
        item4 = csv_data.IngredientData(str(4), "Fourth Name", "Vendor Info 4", str(1), str(33), "Fourth comment")
        data.append(item1)
        data.append(item2)
        data.append(item3)
        data.append(item4)
    elif (test == "product_lines"):
        print("product lines")
    elif (test == "sku_ingredients"):
        print("sku ingredients")
    export_csv(data)
