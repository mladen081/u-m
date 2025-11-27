# config/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from front.views import index

urlpatterns = [
    path("dobrojutro/", admin.site.urls),
    path("api/auth/", include('accounts.urls')),
    re_path(r'^.*$', index, name='index'),
]