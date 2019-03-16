# home/urls.py
from django.conf.urls import url
from home import views
from django.urls import path


urlpatterns = [
    path('', views.index, name='index'),
    path('authin/', views.authin, name='authin'),
    path('invalidlogin/', views.invalidlogin, name='invalidlogin'),
    path('help/', views.help, name='help'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('netlog/', views.netlog, name='netlog'),
    path('netret/', views.netret, name='netret'),
    path('authmid/', views.authmid, name='authmid'),
    path('assistant/', views.assistant, name='assistant'),
    path('cya/', views.cya, name='cya'),
    path('cyaend/', views.cya_end, name='cyaend'),
]
