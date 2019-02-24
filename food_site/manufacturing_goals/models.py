from datetime import timedelta

from django.db import models
from sku_manage.models import Ingredient, ProductLine, SKU, ManufacturingLine, IngredientQty
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

class ScheduleItem(models.Model):
	mfgqty = models.ForeignKey(ManufacturingQty, on_delete=models.PROTECT)
	mfgline = models.ForeignKey(ManufacturingLine, on_delete=models.PROTECT)
	start = models.DateTimeField(blank=True, null=True)

	def clean(self):
		if SkuMfgLine.objects.filter(sku=self.mfgqty.sku, mfg_line=self.mfgline).count() == 0:
			raise ValidationError('Cannot produce selected SKU on manufacturing line')

	def duration(self):
		return timedelta(hours=(self.mfgqty.sku.mfg_rate*self.mfgqty.caseqty))
