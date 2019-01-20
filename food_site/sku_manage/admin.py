from django.contrib import admin

from .models import Ingredient, ProductLine, SKU

class IngredientAdmin(admin.ModelAdmin):
	fields = ['name', 'number', 'package_size', 'cost', 'vendor_info', 'comment']

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(SKU)
admin.site.register(ProductLine)
