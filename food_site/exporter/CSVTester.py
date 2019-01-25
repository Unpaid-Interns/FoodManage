from exporter import CSVExport
from sku_manage import models
from decimal import Decimal


def run():
    exporter = CSVExport.CSVExport()

    # skus.csv export
    data = []
    # number, name, case upc, unit upc, unit size, count per case, product line name, comment
    print("SKUS EXPORT TEST STARTING...")
    item1 = models.SKU(sku_num=1, name="First Name", case_upc=Decimal(1),
               unit_upc=Decimal(1), unit_size="1 lb(s)",
               units_per_case=3, product_line=models.ProductLine(name="Product Line 1"),
               comment="First Comment")
    item2 = models.SKU(sku_num=1, name="Second Name", case_upc=Decimal(1),
                       unit_upc=Decimal(1), unit_size="2 lb(s)",
                       units_per_case=3, product_line=models.ProductLine(name="Product Line 2"),
                       comment="Second Comment")
    item3 = models.SKU(sku_num=1, name="Third Name", case_upc=Decimal(4),
                       unit_upc=Decimal(6), unit_size="1 lb(s)",
                       units_per_case=7, product_line=models.ProductLine(name="Product Line 3"),
                       comment="Third Comment")
    item4 = models.SKU(sku_num=1, name="Fourth Name", case_upc=Decimal(1),
                       unit_upc=Decimal(1), unit_size="13 lb(s)",
                       units_per_case=3, product_line=models.ProductLine(name="Product Line 4"),
                       comment="Fourth Comment")
    data.append(item1)
    data.append(item2)
    data.append(item3)
    data.append(item4)
    exporter.export_to_csv("skus", data)

    # ingredients.csv export
    data = []
    # number, name, vendor_info, package_size, cost, comment
    print("INGREDIENTS EXPORT TEST STARTING...")
    item1 = models.Ingredient(number=1, name="First Name", vendor_info="Vendor Info 1",
                      package_size="4", cost=Decimal("452"), comment="First comment")
    item2 = models.Ingredient(number=2, name="Second Name", vendor_info="Vendor Info 2",
                              package_size="45", cost=Decimal("523"), comment="Second comment")
    item3 = models.Ingredient(number=3, name="Third Name", vendor_info="Vendor Info 3",
                              package_size="24", cost=Decimal("454"), comment="Third comment")
    item4 = models.Ingredient(number=4, name="Fourth Name", vendor_info="Vendor Info 4",
                              package_size="6", cost=Decimal("43"), comment="Fourth comment")
    data.append(item1)
    data.append(item2)
    data.append(item3)
    data.append(item4)
    exporter.export_to_csv("ingredients", data)

    # product_lines.csv export
    data = []
    # name
    print("PRODUCT LINES EXPORT TEST STARTING...")
    item1 = models.ProductLine(name="Product 1")
    item2 = models.ProductLine(name="Product 2")
    print(item2.name)
    item3 = models.ProductLine(name="Product 3")
    item4 = models.ProductLine(name="Product 4")
    data.append(item1)
    data.append(item2)
    data.append(item3)
    data.append(item4)
    exporter.export_to_csv("product_lines", data)

    # sku_ingredients.csv export
    # data = []
    # # sku number, ingredient number, quantity
    # print("SKU INGREDIENTS EXPORT TEST STARTING...")
    # item1 = CSVData.SKUIngredientData(str(1), str(11), str(80085))
    # item2 = CSVData.SKUIngredientData(str(2), str(22), str(8008135))
    # item3 = CSVData.SKUIngredientData(str(3), str(33), str(5812))
    # item4 = CSVData.SKUIngredientData(str(4), str(44), str(12))
    # data.append(item1)
    # data.append(item2)
    # data.append(item3)
    # data.append(item4)
    # exporter.export_to_csv("formula", data)
