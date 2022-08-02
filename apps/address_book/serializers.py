"""Address book application rest framework serializers
"""
from django.contrib.auth.models import User

from rest_framework import serializers

from apps.address_book.models import AddressEntry, FavoriteEntry
  

class AddressEntrySerializer(serializers.ModelSerializer):
  """Address entry serializer with extra param: add_to_favorite - if True then save entry to favorite table.
  """
  add_to_favorite = serializers.BooleanField(read_only=True, default=False)

  class Meta:
    model = AddressEntry
    fields = '__all__'
  

class FavoriteEntrySerializer(serializers.ModelSerializer):
  """Favorite entry serializer
  """
  class Meta:
    model = FavoriteEntry
    fields = '__all__'


class UserDataSerializer(serializers.ModelSerializer):
  """User data serializer
  """
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email', 'last_login', 'date_joined')
    extra_kwargs = {
      'last_login': {'read_only': True},
			'date_joined': {'read_only': True}
    }


class PasswordSerializer(serializers.ModelSerializer):
	"""Password serializer used for password change by account owner
	"""
	old_password = serializers.CharField(required=False) # stare hasło
	class Meta:
		model = User
		fields = ('password', 'old_password')
		extra_kwargs = {
      'password': {'write_only': True},
      'old_password': {'write_only': True}
    }
