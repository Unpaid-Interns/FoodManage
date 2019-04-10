import django_tables2 as tables
from django.contrib.auth.models import User, Group

class UserTable(tables.Table):
	edit = tables.TemplateColumn('<div class="inline"><a class="btn" href="{% url "edituser" record.pk %}"><i class="fa fa-pencil"></i></a></div>')
	email = tables.TemplateColumn('{{ record.email }}')
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'edit']

