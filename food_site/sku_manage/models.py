from django.db import models

class Ingredient(models.Model):
	name = models.CharField(max_length=256, unique=True, verbose_name='Ingredient Name')
	number = models.IntegerField(unique=True, blank=True, verbose_name='Ingredient#')
	vendor_info = models.TextField(blank=True, verbose_name='Vendor Information')
	package_size = models.CharField(max_length=256)
	cost = models.DecimalField(max_digits=12, decimal_places=2)
	comment = models.TextField(blank=True)

	def gen_num(self):
		ingredients = Ingredient.objects.order_by('number')
		for i in range(0, len(ingredients)):
			if(ingredients[i].number > i):
				return i
		return len(ingredients)

	def __str__(self):
		return self.name

	def save(self):
		if self.number == None:
			self.number = self.gen_num()
		super(Ingredient, self).save()

class ProductLine(models.Model):
	name = models.CharField(max_length=256, primary_key=True)

	def __str__(self):
		return self.name


class SKU(models.Model):
	name = models.CharField(max_length=32)
	sku_num = models.IntegerField(unique=True, blank=True, verbose_name='SKU#')
	case_upc = models.DecimalField(max_digits=12, decimal_places=0, unique=True, verbose_name='Case UPC')
	unit_upc = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Unit UPC')
	unit_size = models.CharField(max_length=256)
	units_per_case = models.IntegerField()
	product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT)
	comment = models.TextField(blank=True)

	def check_case_upc(self):
		upc_str = '0' * (12-len(str(self.case_upc))) + str(self.case_upc)
		if 0 < int(upc_str[0]) < 6:
			return False
		sum_val = 0
		for i in range(0, 6):
			sum_val += int(upc_str[i*2])
		sum_val = sum_val * 3
		for i in range(0, 6):
			sum_val += int(upc_str[i*2 + 1])
		return sum_val % 10 == 0

	def check_unit_upc(self):
		upc_str = '0' * (12-len(str(self.unit_upc))) + str(self.unit_upc)
		if 0 < int(upc_str[0]) < 6:
			return False
		sum_val = 0
		for i in range(0, 6):
			sum_val += int(upc_str[i*2])
		sum_val = sum_val * 3
		for i in range(0, 6):
			sum_val += int(upc_str[i*2 + 1])
		return sum_val % 10 == 0

	def gen_num(self):
		skus = SKU.objects.order_by('sku_num')
		for i in range(0, len(skus)):
			if(skus[i].sku_num > i):
				return i
		return len(skus)

	def __str__(self):
		return "{name}: {unit_size} * {units_per_case}".format(name=self.name, unit_size=self.unit_size, units_per_case=self.units_per_case)

	def save(self):
		if self.sku_num == None:
			self.sku_num = self.gen_num()
		super(SKU, self).save()


class IngredientQty(models.Model):
	sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
	quantity = models.DecimalField(max_digits=20, decimal_places=10)
