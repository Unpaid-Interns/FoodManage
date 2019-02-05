from django.contrib import admin
from .models import ManufacturingQty, ManufacturingGoal

class ManufacturingQtyInline(admin.TabularInline):
	model = ManufacturingQty
	extra = 0

class ManufacturingGoalAdmin(admin.ModelAdmin):
	fields = ['name','user']
	inlines = [ManufacturingQtyInline]

admin.site.register(ManufacturingGoal, ManufacturingGoalAdmin)
