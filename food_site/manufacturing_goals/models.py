from datetime import datetime, time, timedelta
import time as sys_time

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
	last_edit = models.FloatField(default=sys_time.time(), verbose_name='Last Edit Timestamp')
	deadline = models.DateField()
	enabled = models.BooleanField(default=False)

	class Meta:
		permissions = (('enable_manufacturinggoal', 'Can enable/disable manufacturing goals'),)
	
	def save(self, *args, **kwargs):
		self.last_edit = sys_time.time()
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name

class ManufacturingQty(models.Model):
	sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='SKU')
	caseqty = models.FloatField(verbose_name='Case Quantity')
	goal = models.ForeignKey(ManufacturingGoal, on_delete=models.CASCADE)

class ScheduleItem(models.Model):
	mfgqty = models.ForeignKey(ManufacturingQty, on_delete=models.CASCADE)
	mfgline = models.ForeignKey(ManufacturingLine, on_delete=models.CASCADE)
	start = models.DateTimeField(validators=[validate_workday], blank=True, null=True)
	endoverride = models.DateTimeField(validators=[validate_workday], blank=True, null=True)
	provisional_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

	def clean(self):
		if SkuMfgLine.objects.filter(sku=self.mfgqty.sku, mfg_line=self.mfgline).count() == 0:
			raise ValidationError('Cannot produce selected SKU on manufacturing line')

	def duration(self):
		if (self.mfgqty.caseqty/self.mfgqty.sku.mfg_rate) < 1:
			return timedelta(hours=1)
		return timedelta(hours=(self.mfgqty.caseqty/self.mfgqty.sku.mfg_rate))

	def end_calc(self):
		endtime = self.start + self.duration()
		index = self.start.replace(hour=18, tzinfo=timezone.get_current_timezone())
		while index < endtime:
			endtime += timedelta(hours=14)
			index += timedelta(days=1)
		return endtime

	def end(self):
		if self.endoverride is not None:
			return self.endoverride
		return self.end_calc()

	def too_late(self):
		return datetime.combine(self.mfgqty.goal.deadline, time.max).replace(tzinfo=timezone.get_current_timezone()) < self.end()

	def start_time(self):
		return self.start.strftime("%Y-%m-%dT%H:%M:%S%z")

	def end_time(self):
		return self.end().strftime("%Y-%m-%dT%H:%M:%S%z")

	def __str__(self):
		return str(self.mfgqty.goal.name) + ': ' + self.mfgqty.sku.name + ', due by ' + '{:%Y-%m-%d}'.format(self.mfgqty.goal.deadline)


