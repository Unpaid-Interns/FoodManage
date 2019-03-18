from django.contrib import admin
from sku_manage.admin import admin_site
from .models import Customer, SalesRecord

admin_site.register(Customer)
admin_site.register(SalesRecord)
