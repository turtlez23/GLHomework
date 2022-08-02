"""Admin site configuration
"""
from django.conf import settings
from django.contrib import admin

from apps.address_book.models import AddressEntry, FavoriteEntry

# Change admin page metadata
admin.site.site_header = settings.ADMIN_SITE_TITLE
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_SITE_TITLE

# Register admin pages using models
admin.site.register(AddressEntry)
admin.site.register(FavoriteEntry)
