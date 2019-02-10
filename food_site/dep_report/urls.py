# dep_report/urls.py
from django.conf.urls import url
from dep_report import views
from django.urls import path

urlpatterns = [
	path('ingredient/', views.ingr_dep_menu, name='ingr_dep'),
	path('ingredient/report/', views.ingr_dep_report, name='ingr_dep_report'),
]
