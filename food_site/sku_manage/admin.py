from django.contrib import admin

from .models import Ingredient, ProductLine, SKU, IngredientQty

class IngredientAdmin(admin.ModelAdmin):
	fields = ['name', 'package_size', 'cost', 'vendor_info', 'comment']

class IngredientQtyInline(admin.TabularInline):
	model = IngredientQty
	extra = 2

class SkuAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['name', 'product_line']}),
		('UPC Information', {'fields': ['case_upc', 'unit_upc']}),
		('Size Information', {'fields': ['unit_size', 'units_per_case']}),
		('', {'fields': ['comment']}),
	]
	inlines = [IngredientQtyInline]

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(SKU, SkuAdmin)
admin.site.register(ProductLine)
