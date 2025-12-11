# config/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from front.views import index

urlpatterns = [
    path("dobrojutro/", admin.site.urls),
    path("api/auth/", include('accounts.urls')),
    path("api/chat/", include('chat.urls')),
    re_path(r'^.*$', index, name='index'),
]