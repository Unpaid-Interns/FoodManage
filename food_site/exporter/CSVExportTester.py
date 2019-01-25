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
    item3 = models.ProductLine(name="Product 3")
    item4 = models.ProductLine(name="Product 4")
    data.append(item1)
    data.append(item2)
    data.append(item3)
    data.append(item4)
    exporter.export_to_csv("product_lines", data)

    # formula.csv export
    data = []
    # sku number, ingredient number, quantity
    print("SKU INGREDIENTS EXPORT TEST STARTING...")
    item1 = models.IngredientQty(sku=models.SKU(sku_num=1), ingredient=models.Ingredient(number=11),
                                 quantity=Decimal(80085))
    item2 = models.IngredientQty(sku=models.SKU(sku_num=2), ingredient=models.Ingredient(number=22),
                                 quantity=Decimal(80085135))
    item3 = models.IngredientQty(sku=models.SKU(sku_num=3), ingredient=models.Ingredient(number=33),
                                 quantity=Decimal(5812))
    item4 = models.IngredientQty(sku=models.SKU(sku_num=4), ingredient=models.Ingredient(number=44),
                                 quantity=Decimal(12))
    data.append(item1)
    data.append(item2)
    data.append(item3)
    data.append(item4)
    exporter.export_to_csv("formula", data)
