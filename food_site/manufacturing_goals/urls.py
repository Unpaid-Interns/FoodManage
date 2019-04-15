from django.conf.urls import url
from manufacturing_goals import views
from django.urls import path

urlpatterns = [
	path('', views.manufacturing, name='manufacturing'),
	path('timeline/edit/', views.timeline, name='timeline'),
	path('timeline/', views.timeline_viewer, name='timeline_viewer'),
	path('manufqty/', views.manufqty, name='manufqty'),
	path('manufdetails/', views.manufdetails, name='manufdetails'),
	path('add/<int:pk>/', views.goal_add, name='mfg_goal_add'),
	path('remove/<int:pk>/', views.goal_remove, name='mfg_goal_remove'),
	path('enable/', views.enable_menu, name='enable_menu'),
	path('projection/<int:pk>/', views.project, name='projection'),
	path('dateset/', views.set_project_date, name='dateset'),
	path('enable/<int:pk>/', views.enable_goal, name='enable_goal'),
	path('timeline/autoschedule/', views.auto_schedule_select, name='auto_schedule_select'),
	path('timeline/autoschedule/add/<int:pk>/', views.auto_schedule_add, name='autoschedule_add'),
	path('timeline/autoschedule/remove/<int:pk>/', views.auto_schedule_remove, name='autoschedule_remove'),
	path('timeline/autoschedule/run/', views.auto_schedule, name='auto_schedule'),
]
