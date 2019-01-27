from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib import admin

from .models import Ingredient, ProductLine, SKU, IngredientQty

class MainAdmin(admin.AdminSite):
	site_header = 'Hypothetical Meals'
	site_title = 'Hypothetical Admin'
	index_title = 'Hypothetical Meals Administration'


class IngredientAdmin(admin.ModelAdmin):
	fields = ['name', 'number', 'package_size', 'cost', 'vendor_info', 'comment']
	list_display = ('name', 'number', 'package_size', 'cost')
	search_fields = ['name', 'number']

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
	list_filter = ['product_line']
	search_fields = ['name', 'sku_num']

admin_site = MainAdmin(name='food_site_admin')
admin_site.register(Ingredient, IngredientAdmin)
admin_site.register(SKU, SkuAdmin)
admin_site.register(ProductLine)
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
