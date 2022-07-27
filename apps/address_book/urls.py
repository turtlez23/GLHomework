from django.urls import path
from apps.address_book.views import  home_page

urlpatterns = [
    path('', home_page, name='home_page'),
]