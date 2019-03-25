from django.urls import path

from . import views

urlpatterns = [
    path('', views.simple_upload, name='simple_upload'),
    path('messages/', views.message_displayer, name='message_displayer'),
    path('messages/<int:messagenum>/', views.commit_to_database, name='commit_to_database'),
    path('messages/all/', views.commit_all_to_database, name='commit_all_to_database'),
    path('help/', views.info, name='info')
]
