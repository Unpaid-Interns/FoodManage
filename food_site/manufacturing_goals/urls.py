from django.conf.urls import url
from manufacturing_goals import views
from django.urls import path

urlpatterns = [
	path('', views.manufacturing, name='manufacturing'),
	path('timeline/', views.timeline, name='timeline'),
	path('manufqty/', views.manufqty, name='manufqty'),
	path('manufdetails/', views.manufdetails, name='manufdetails'),
	path('add/<int:pk>', views.goal_add, name='mfg_goal_add'),
	path('remove/<int:pk>', views.goal_remove, name='mfg_goal_remove'),
	path('enable/', views.enable_menu, name='enable_menu'),
	path('enable/<int:pk>', views.enable_goal, name='enable_goal'),
	path('projection/<int:pk>', views.project, name='projection'),
	path('dateset', views.set_project_date, name='dateset'),
]
