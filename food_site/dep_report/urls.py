# dep_report/urls.py
from django.conf.urls import url
from dep_report import views
from django.urls import path

urlpatterns = [
	path('ingredient/', views.ingr_dep_menu, name='ingr_dep'),
	path('ingredient/add/<int:pk>/', views.ingr_dep_add, name='ingr_dep_add'),
	path('ingredient/remove/<int:pk>/', views.ingr_dep_remove, name='ingr_dep_remove'),
	path('ingredient/generate/', views.ingr_dep_generate, name='ingr_dep_gen'),
	path('ingredient/report/', views.ingr_dep_report, name='ingr_dep_report'),
	path('ingredient/report/download', views.ingr_dep_download, name='ingr_dep_download'),
	path('manufacturing/', views.mfg_sch_menu, name='mfg_sch'),
	path('manufacturing/report/<int:pk>/', views.schedule_report, name='mfg_sch_report'),
	path('manufacturing/report/<int:pk>/print', views.mfg_sch_print, name='mfg_sch_print'),
]
