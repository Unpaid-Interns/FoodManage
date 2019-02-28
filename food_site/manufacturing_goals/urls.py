from django.conf.urls import url
from manufacturing_goals import views
from django.urls import path

urlpatterns = [
	path('manufacturing/', views.manufacturing, name='manufacturing'),
	path('manufacturing/timeline/', views.timeline, name='timeline'),
	path('manufacturing/manufqty/', views.manufqty, name='manufqty'),
	path('manufacturing/manufdetails/', views.manufdetails, name='manufdetails'),
	path('manufacturing/add/<int:pk>', views.goal_add, name='mfg_goal_add'),
	path('manufacturing/remove/<int:pk>', views.goal_remove, name='mfg_goal_remove'),
	path('manufacturing/enable/', views.enable_menu, name='enable_menu'),
	path('manufacturing/enable/<int:pk>', views.enable_goal, name='enable_goal'),
]
