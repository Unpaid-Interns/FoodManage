from django.db import models
from django.core.exceptions import ValidationError

def validate_upc(value):
	if value < 0:
		raise ValidationError('UPC cannot be negative')
	upc_str = '0' * (12-len(str(value))) + str(value)
	if 0 < int(upc_str[0]) < 6:
		raise ValidationError('UPC first digit is not valid')
	sum_val = 0
	for i in range(0, 6):
		sum_val += int(upc_str[i*2])
	sum_val = sum_val * 3
	for i in range(0, 6):
		sum_val += int(upc_str[i*2 + 1])
	if sum_val % 10 != 0:
		raise ValidationError('UPC check digit is not valid')

def validate_positive(value):
	if value < 0:
		raise ValidationError('Must be positive')

def validate_gt_zero(value):
	if value <= 0:
		raise ValidationError('Must be greater than zero')

class Ingredient(models.Model):
	name = models.CharField(max_length=256, unique=True, verbose_name='Ingredient Name')
	number = models.IntegerField(unique=True, blank=True, validators=[validate_positive], verbose_name='Ingredient#')
	vendor_info = models.TextField(blank=True, verbose_name='Vendor Information')
	package_size = models.CharField(max_length=256)
	cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_gt_zero])
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
	case_upc = models.DecimalField(max_digits=12, decimal_places=0, unique=True, validators=[validate_upc], verbose_name='Case UPC')
	unit_upc = models.DecimalField(max_digits=12, decimal_places=0, validators=[validate_upc], verbose_name='Unit UPC')
	unit_size = models.CharField(max_length=256)
	units_per_case = models.IntegerField(validators=[validate_gt_zero])
	product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT)
	comment = models.TextField(blank=True)

	def get_case_upc(self):
		return '0' * (12-len(str(self.case_upc))) + str(self.case_upc)

	def get_unit_upc(self):
		return '0' * (12-len(str(self.unit_upc))) + str(self.unit_upc)

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
	quantity = models.DecimalField(max_digits=20, decimal_places=10, validators=[validate_gt_zero])

	def get_qty(self):
		s = str(self.quantity)
		return s.rstrip('0').rstrip('.') if '.' in s else s
