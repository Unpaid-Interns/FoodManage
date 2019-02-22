# mfg_map/urls.py
from django.urls import path
from . import views

urlpatterns = [
	path('', views.map_view, name='map_view'),
	path('add/<int:pk>', views.map_add, name='mfg_map_add'),
	path('rem/<int:pk>', views.map_remove, name='mfg_map_remove'),
	path('editmapping', views.edit_mapping, name='edit_mapping'),
]
