from django.db import models

class Ingredient(models.Model):
	name = models.CharField(max_length=256, unique=True)
	number = models.AutoField(primary_key=True)
	vendor_info = models.TextField()
	package_size = models.CharField(max_length=256)
	cost = models.DecimalField(max_digits=None, decimal_places=2)
	comment = models.TextField()

	def __str__(self):
		return self.name

class ProductLine(models.Model):
	name = models.CharField(max_length=256, primary_key=True)

class SKU(models.Model):
	name = models.CharField(max_length=32)
	sku_num = models.AutoField(primary_key=True)
	case_upc = models.DecimalField(max_digits=12, decimal_places=0, unique=True)
	unit_upc = models.DecimalField(max_digits=12, decimal_places=0)
	unit_size = models.CharField(max_length=256)
	units_per_case = models.IntegerField()
	product_line = models.ForeignKey(ProductLine, on_delete=models.SET_NULL)
	# Ingredients
	comment = models.TextField()
