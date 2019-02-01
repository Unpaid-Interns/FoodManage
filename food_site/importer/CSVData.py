from decimal import Decimal
from sku_manage import models
import json

headerDict = {
    "skus.csv": ["SKU#", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Ingr#", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formulas.csv": ["SKU#", "Ingr#", "Quantity"]
}

validFilePrefixes = ["skus", "ingredients", "product_lines", "formulas"]


class SKUData:
    def __init__(self, sku_number, name, case_upc, unit_upc, unit_size, case_count, product_line, comment):
        self.name = name
        self.sku_number = sku_number
        self.case_upc = case_upc
        self.unit_upc = unit_upc
        self.unit_size = unit_size
        self.product_line = product_line
        self.case_count = case_count
        self.comment = comment

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __str__(self):
        return "SKUDataObject: Name = " + self.name + ", Num = " + self.sku_number + ", Case UPC = " \
               + self.case_upc + ", Unit UPC = " + self.unit_upc + ", Unit Size = " + self.unit_size \
               + ", Count per case = " + self.case_count + ", Product Line = " + self.product_line + \
               ", Comment = '" + self.comment + "'"

    def convert_to_database_model(self, chosen_product_line):
        return models.SKU(sku_num=int(self.sku_number), name=self.name, case_upc=Decimal(self.case_upc),
                          unit_upc=Decimal(self.unit_upc), unit_size=self.unit_size,
                          units_per_case=int(self.case_count), product_line=chosen_product_line,
                          comment=self.comment)

    def convert_to_string_array(self):
        return [self.sku_number, self.name, self.case_upc, self.unit_upc, self.unit_size,
                self.product_line, self.case_count, self.comment]


class IngredientData:
    def __init__(self, number, name, vendor_info, package_size, cost, comment):
        self.name = name
        self.number = number
        self.vendor_info = vendor_info
        self.package_size = package_size
        self.cost = cost
        self.comment = comment

    def __str__(self):
        return "IngredientsDataObject: Name = " + self.name + ", Num = " + self.number + ", Vendor Info = " \
               + self.vendor_info + ", Package Size = " + self.package_size + ", Cost = " + self.cost \
               + ", Comment = '" + self.comment + "'"

    def convert_to_database_model(self):
        return models.Ingredient(number=int(self.number), name=self.name, vendor_info=self.vendor_info,
                                 package_size=self.package_size, cost=Decimal(self.cost), comment=self.comment)

    def convert_to_string_array(self):
        return [self.number, self.names, self.vendor_info, self.package_size, self.cost, self.comment]

class ProductLineData:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "ProductLineDataObject: Name = " + self.name

    def convert_to_database_model(self):
        return models.ProductLine(name=self.name)

    def convert_to_string_array(self):
        return [self.name]


class SKUIngredientData:
    def __init__(self, sku_number, ingredient_number, quantity):
        self.sku_number = sku_number
        self.ingredient_number = ingredient_number
        self.quantity = quantity

    def __str__(self):
        return "SKUIngredientDataObject: SKU Number = " + self.sku_number + ", Ingredient Number = " \
               + self.ingredient_number + ", Quantity = " + self.quantity

    def convert_to_database_model(self, chosen_sku, chosen_ingredient):
        return models.IngredientQty(sku=chosen_sku, ingredient=chosen_ingredient,
                                    quantity=Decimal(self.quantity))

    def convert_to_string_array(self):
        return [self.sku_number, self.ingredient_number, self.quantity]
