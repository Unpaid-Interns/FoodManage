from django.db import models

class Ingredient(models.Model):
	name = models.CharField(max_length=256, unique=True)
	number = models.AutoField(primary_key=True)
	vendor_info = models.TextField(blank=True)
	package_size = models.CharField(max_length=256)
	cost = models.DecimalField(max_digits=12, decimal_places=2)
	comment = models.TextField(blank=True)

	def __str__(self):
		return self.name

class ProductLine(models.Model):
	name = models.CharField(max_length=256, primary_key=True)

	def __str__(self):
		return self.name

class SKU(models.Model):
	name = models.CharField(max_length=32)
	sku_num = models.AutoField(primary_key=True)
	case_upc = models.DecimalField(max_digits=12, decimal_places=0, unique=True)
	unit_upc = models.DecimalField(max_digits=12, decimal_places=0)
	unit_size = models.CharField(max_length=256)
	units_per_case = models.IntegerField()
	product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT)
	comment = models.TextField(blank=True)

	def __str__(self):
		return "{name}: {unit_size} * {units_per_case}".format(name=self.name, unit_size=self.unit_size, units_per_case=self.units_per_case) 

class IngredientQty(models.Model):
	sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
	quantity = models.DecimalField(max_digits=20, decimal_places=10)
	
