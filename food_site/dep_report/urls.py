# dep_report/urls.py
from django.conf.urls import url
from dep_report import views
from django.urls import path

urlpatterns = [
	path('ingredient/', views.IngredientDependency, name='ingredient_dep'),
]
