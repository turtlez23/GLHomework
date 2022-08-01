from django.contrib import admin

from apps.address_book.models import AddressEntry, FavouriteEntry

# Change admin page metadata
admin.site.site_header = "Address book" 
admin.site.site_title = "Address book"
admin.site.index_title = "Address book"

# Register admin pages for models
admin.site.register(AddressEntry)
admin.site.register(FavouriteEntry)
