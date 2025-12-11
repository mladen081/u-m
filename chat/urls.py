# chat/urls.py

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('messages/', views.get_messages, name='get_messages'),
]