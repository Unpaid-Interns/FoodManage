from django.contrib import admin

from .models import Ingredient, ProductLine, SKU, IngredientQty

class IngredientAdmin(admin.ModelAdmin):
	fields = ['name', 'number', 'package_size', 'cost', 'vendor_info', 'comment']
	list_display = ('name', 'number', 'package_size', 'cost')

class IngredientQtyInline(admin.TabularInline):
	model = IngredientQty
	extra = 2

class SkuAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['name', 'sku_num', 'product_line']}),
		('UPC Information', {'fields': ['case_upc', 'unit_upc']}),
		('Size Information', {'fields': ['unit_size', 'units_per_case']}),
		('Comments', {'fields': ['comment'], 'classes': ['collapse']}),
	]
	inlines = [IngredientQtyInline]
	list_display = ('__str__', 'sku_num', 'product_line')

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(SKU, SkuAdmin)
admin.site.register(ProductLine)
