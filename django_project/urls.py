"""Django project URL Configuration
"""
from django.conf.urls import url

from django.contrib import admin
from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view

from apps.address_book import urls as address_book_urls


# Routing config
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(address_book_urls)),
]

# Add swagger docs
swqgger_schema_view = get_swagger_view(title='Portal API')
urlpatterns.extend([url(r'^api/rest/v1/docs$', swqgger_schema_view)])