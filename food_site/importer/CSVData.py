from decimal import Decimal
from sku_manage import models

headerDict = {
    "skus.csv": ["Number", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Number", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "formula.csv": ["SKU Number", "Ingredient Number", "Quantity"]
}

validFilePrefixes = ["skus", "ingredients", "product_lines", "formula"]


class SKUData:
    def __init__(self, sku_number, name, case_upc, unit_upc, unit_size, case_count, product_line, comment):
        self.exportData = []
        self.exportData.append(sku_number)
        self.exportData.append(name)
        self.exportData.append(case_upc)
        self.exportData.append(unit_upc)
        self.exportData.append(unit_size)
        self.exportData.append(case_count)
        self.exportData.append(product_line)
        self.exportData.append(comment)
        self.name = name
        self.sku_number = sku_number
        self.case_upc = case_upc
        self.unit_upc = unit_upc
        self.unit_size = unit_size
        self.product_line = product_line
        self.case_count = case_count
        self.comment = comment

    def __str__(self):
        return "SKUDataObject: Name = " + self.name + ", Num = " + self.sku_number + ", Case UPC = " \
               + self.case_upc + ", Unit UPC = " + self.unit_upc + ", Unit Size = " + self.unit_size \
               + ", Count per case = " + self.case_count + ", Product Line = " + self.product_line + \
               ", Comment = '" + self.comment + "'"

    def convert_to_database_model(self, product_line_dict):
        return models.SKU(sku_num=int(self.sku_number), name=self.name, case_upc=Decimal(self.case_upc),
                          unit_upc=Decimal(self.unit_upc), unit_size=self.unit_size,
                          units_per_case=int(self.case_count), product_line=product_line_dict[self.product_line],
                          comment=self.comment)


class IngredientData:
    def __init__(self, number, name, vendor_info, package_size, cost, comment):
        self.exportData = []
        self.exportData.append(number)
        self.exportData.append(name)
        self.exportData.append(vendor_info)
        self.exportData.append(package_size)
        self.exportData.append(cost)
        self.exportData.append(comment)
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


class ProductLineData:
    def __init__(self, name):
        self.exportData = []
        self.exportData.append(name)
        self.name = name

    def __str__(self):
        return "ProductLineDataObject: Name = " + self.name

    def convert_to_database_model(self):
        return models.ProductLine(name=self.name)


class SKUIngredientData:
    def __init__(self, sku_number, ingredient_number, quantity):
        self.exportData = []
        self.exportData.append(sku_number)
        self.exportData.append(ingredient_number)
        self.exportData.append(quantity)
        self.sku_number = sku_number
        self.ingredient_number = ingredient_number
        self.quantity = quantity

    def __str__(self):
        return "SKUIngredientDataObject: SKU Number = " + self.sku_number + ", Ingredient Number = " \
               + self.ingredient_number + ", Quantity = " + self.quantity

    def convert_to_database_model(self, sku_list, ingredient_list):
        # return models.IngredientQty(sku=int(self.sku_number), ingredient=int(self.ingredient_number),
        #                             quantity=Decimal(self.quantity))
        chosen_sku_model = None
        chosen_ing_model = None
        for sku_model in sku_list:
            if sku_model.sku_num == int(self.sku_number):
                chosen_sku_model = sku_model
        for ing_model in ingredient_list:
            if ing_model.number == int(self.ingredient_number):
                chosen_ing_model = ing_model
        return models.IngredientQty(sku=chosen_sku_model, ingredient=chosen_ing_model,
                                    quantity=Decimal(self.quantity))
