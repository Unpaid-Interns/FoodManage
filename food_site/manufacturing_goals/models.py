from django.db import models
from sku_manage.models import Ingredient, ProductLine, SKU, IngredientQty
from django.contrib.auth.models import User

class ManufacturingGoal(models.Model):
	name = models.CharField(max_length=500)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	deadline = models.DateField()
	
	def __str__(self):
		return self.name

class ManufacturingQty(models.Model):
	sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='SKU')
	caseqty = models.DecimalField(max_digits=20, decimal_places=10, verbose_name='Case Quantity')
	goal = models.ForeignKey(ManufacturingGoal, on_delete=models.CASCADE)

class ScheduleItem(mdoels.Model):
	mfgqty = models.ForeignKey(ManufacturingQty, on_delete=models.PROTECT)
	start = models.DateTimeField()