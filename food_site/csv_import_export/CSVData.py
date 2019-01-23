headerDict = {
    "skus.csv": ["Number", "Name", "Case UPC", "Unit UPC", "Unit size", "Count per case", "Product Line Name",
                 "Comment"],
    "ingredients.csv": ["Number", "Name", "Vendor Info", "Size", "Cost", "Comment"],
    "product_lines.csv": ["Name"],
    "sku_ingredients.csv": ["SKU Number", "Ingredient Number", "Quantity"]
}

validFilePrefixes = ["skus", "ingredients", "product_lines", "sku_ingredients"]


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


class ProductLineData:
    def __init__(self, name):
        self.exportData = []
        self.exportData.append(name)
        self.name = name

    def __str__(self):
        return "ProductLineDataObject: Name = " + self.name


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


class BundledData:
    def __init__(self):
        self.sku = None
        self.ingredient = None
        self.productLine = None
        self.skuIngredient = None

    def __init__(self, sku, skuIngredient, productLine, ingredient):
        self.sku = sku
        self.ingredient = ingredient
        self.productLine = productLine
        self.skuIngredient = skuIngredient

    def add_sku_data(self, sku):
        self.sku = sku

    def add_skuIngredient_data(self, skuIngredient):
        self.skuIngredient = skuIngredient

    def add_productLine_data(self, productLine):
        self.productLine = productLine

    def add_ingredient_data(self, ingredient):
        self.ingredient = ingredient