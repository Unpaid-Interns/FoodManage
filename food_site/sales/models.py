from django.db import models
from sku_manage.models import SKU, validate_gt_zero

class Customer(models.Model):
    name = models.CharField(max_length=256, verbose_name="Customer Name")
    number = models.IntegerField(unique=True, verbose_name='Customer#')

    def __str__(self):
        return self.name

class SalesRecord(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cases_sold = models.IntegerField(validators=[validate_gt_zero])
    price_per_case = models.DecimalField(max_digits=12, decimal_places=2, validators=[validate_gt_zero])

    class Meta:
    	permissions = (('report_salesrecord', 'Can view sales reports'),)
