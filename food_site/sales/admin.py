from django.contrib import admin
from sku_manage.admin import admin_site
from .models import Customer, SalesRecord

from background_task.models import Task
from background_task.admin import TaskAdmin, CompletedTaskAdmin
from background_task.models_completed import CompletedTask

admin_site.register(Customer)
admin_site.register(SalesRecord)

admin_site.register(Task, TaskAdmin)
admin_site.register(CompletedTask, CompletedTaskAdmin)
