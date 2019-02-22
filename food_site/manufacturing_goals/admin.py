from django.contrib import admin
from .models import ManufacturingQty, ManufacturingGoal
from sku_manage.admin import admin_site

class ManufacturingQtyInline(admin.TabularInline):
	model = ManufacturingQty
	extra = 0

class ManufacturingGoalAdmin(admin.ModelAdmin):
	fields = ['name','user','deadline']
	inlines = [ManufacturingQtyInline]

admin_site.register(ManufacturingGoal, ManufacturingGoalAdmin)
