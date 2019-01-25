# sku_manage/urls.py
from django.conf.urls import url
from sku_manage import views
from django.urls import path

urlpatterns = [
	path('data/', views.data, name='data'),
]
