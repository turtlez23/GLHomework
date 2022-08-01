"""django_project URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from apps.address_book import urls as address_book_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(address_book_urls)),
]
