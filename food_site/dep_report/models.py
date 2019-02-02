from django.db import models
from sku_manage.models import Ingredient

# Create your models here.
class IngredientList(models.Model):
	list_id = models.IntegerField()
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

	def gen_new_id(self):
		ids = IngredientList.objects.order_by('list_id')
		for i in range(0, len(ids)):
			if(ids[i].number > i):
				return i
		return len(ids)
