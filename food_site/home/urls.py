# home/urls.py
from django.conf.urls import url
from home import views
from django.urls import path


urlpatterns = [
    path('', views.index, name='index'),
    path('authin/', views.authin, name='authin'),
    path('authout/', views.authout, name='authout'),
]
