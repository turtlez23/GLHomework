from django.shortcuts import render
from django.conf import settings




def home_page(request):
  return render(request, "address_book/home.html", {'title': settings.ADDRESS_BOOK_TITLE})