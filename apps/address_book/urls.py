"""Django address_book app URLs configuration
"""
from django.urls import path, include

from rest_framework import routers

from apps.address_book.views import home_page, AddressEntryViewSet, FavoriteEntryViewSet, AboutView, UserDataViewSet

# Register DRF router
restRouter = routers.DefaultRouter()
restRouter.register('address_entries', AddressEntryViewSet)
restRouter.register('favorite_entries', FavoriteEntryViewSet)
restRouter.register('users', UserDataViewSet)

# Routing config
urlpatterns = [
    path('', home_page, name='home_page'),
    path('about/', AboutView.as_view(), name='about_page'),
    path('api/rest/v1/', include(restRouter.urls), name='api_rest_v1'),
]
