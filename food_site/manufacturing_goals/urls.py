from django.conf.urls import url
from manufacturing_goals import views
from django.urls import path

urlpatterns = [
	path('manufacturing/', views.manufacturing, name='manufacturing'),
	path('manufacturing/timeline/', views.timeline, name='timeline'),
	path('manufacturing/manufqty/', views.manufqty, name='manufqty'),
	path('manufacturing/manufdetails/', views.manufdetails, name='manufdetails'),
]
