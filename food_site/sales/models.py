from django.db import models
from sku_manage.models import SKU

class SalesRecord(models.Model):
	sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
	date = models.DateField()
	customer_num = models.IntegerField()
	customer_name = models.CharField(max_length=256)
	cases_sold = models.IntegerField(validators=[validate_gt_zero])
    price_per_case = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_gt_zero])
