from datetime import datetime, timedelta

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from sku_manage.models import Ingredient, ProductLine, SKU, ManufacturingLine, IngredientQty, SkuMfgLine
from django.contrib.auth.models import User

def validate_workday(value):
	if value.hour < 8 or value.hour > 18:
		raise ValidationError('Manufacturing start time outside of workday')

class ManufacturingGoal(models.Model):
	name = models.CharField(max_length=500)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	deadline = models.DateField()
	
	def __str__(self):
		return self.name

class ManufacturingQty(models.Model):
	sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='SKU')
	caseqty = models.FloatField(verbose_name='Case Quantity')
	goal = models.ForeignKey(ManufacturingGoal, on_delete=models.CASCADE)

class ScheduleItem(models.Model):
	mfgqty = models.ForeignKey(ManufacturingQty, on_delete=models.PROTECT)
	mfgline = models.ForeignKey(ManufacturingLine, on_delete=models.PROTECT)
	start = models.DateTimeField(validators=[validate_workday])

	def clean(self):
		if SkuMfgLine.objects.filter(sku=self.mfgqty.sku, mfg_line=self.mfgline).count() == 0:
			raise ValidationError('Cannot produce selected SKU on manufacturing line')

	def duration(self):
		return timedelta(hours=(self.mfgqty.sku.mfg_rate*self.mfgqty.caseqty))

	def end(self):
		endtime = self.start + self.duration()
		index = self.start.replace(hour=18, tzinfo=timezone.get_current_timezone())
		while index < endtime:
			endtime += timedelta(hours=14)
			index += timedelta(days=1)
		return endtime


