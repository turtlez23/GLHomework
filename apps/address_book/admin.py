from django.contrib import admin

from apps.address_book.models import AddressEntry, FavouriteEntry

# Change admin page metadata
admin.site.site_header = "Address book" 
admin.site.site_title = "Address book"
admin.site.index_title = "Address book"

# Register admin pages for models
admin.site.register(AddressEntry)
admin.site.register(FavouriteEntry)





# # delete all private entries
# FavouriteEntry.objects.all().filter(user=request.user, address_entry__share=AddressEntry.PRIVATE_SHARE).delete()

# # change user owner to None
# FavouriteEntry.objects.all().filter(user=request.user, address_entry__share=AddressEntry.PUBLIC_SHARE).update(user=None)