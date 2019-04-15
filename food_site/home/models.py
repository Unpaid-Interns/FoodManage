from django.db import models
from django.contrib.auth.models import User
from sku_manage.models import ManufacturingLine

class PlantManager(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	mfgline = models.ForeignKey(ManufacturingLine, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user) + " -> " + str(self.mfgline)