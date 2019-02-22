from django.conf.urls import url
from manufacturing_goals import views
from django.urls import path

urlpatterns = [
	path('manufacturing/', views.manufacturing, name='manufacturing'),
	path('manufacturing/manufqty/', views.manufqty, name='manufqty'),
	path('manufacturing/manufdetails/', views.manufdetails, name='manufdetails'),
	path('manufacturing/manufcalc/', views.manufcalc, name='manufcalc'),
	path('manufacturing/manufcalc/calcresults/', views.calcresults, name='calcresults'),
	path('manufacturing/manufcsv/', views.manufcsv, name='manufcsv'),
	path('manufacturing/manufcsv/manufexport/', views.manufexport, name='manufexport'),
]
