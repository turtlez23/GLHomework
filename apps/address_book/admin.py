from django.contrib import admin

from apps.address_book.models import AddressEntry, FavouriteEntry

admin.site.register(AddressEntry)
admin.site.register(FavouriteEntry)