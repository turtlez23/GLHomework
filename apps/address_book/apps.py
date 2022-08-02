"""App configuration
"""
from django.apps import AppConfig


class AddressBookConfig(AppConfig):
    """Address book app config
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.address_book'
