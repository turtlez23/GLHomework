from rest_framework import serializers

from apps.address_book.models import AddressEntry, FavouriteEntry
from django.contrib.auth.models import User
  
class AddressEntrySerializer(serializers.ModelSerializer):
  """Address entry serializer with extra params:
  add_to_favourite - check if address entry has to save to favourite db table.
  """
  add_to_favourite = serializers.BooleanField(read_only=True, default=False)

  class Meta:
    model = AddressEntry
    # fields = ('name', 'lastname', 'middlename', 'nickname', 'phone', 'mobile_phone', 'email', 'company', 'position', 'added_by', 'addToFavourite')
    fields = '__all__'
  
class FavouriteEntrySerializer(serializers.ModelSerializer):
  """Favourite entry serializer
  """
  class Meta:
    model = FavouriteEntry
    fields = '__all__'


class UserDataSerializer(serializers.ModelSerializer):
  """Favourite entry serializer
  """
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email', 'last_login', 'date_joined')
    extra_kwargs = {
      'last_login': {'read_only': True},
			'date_joined': {'read_only': True}
    }

class PasswordSerializer(serializers.ModelSerializer):
	"""Serializer webservices - User - edycja hasła użytkownika
	Pozwala na walidację, organizację przesyłanych danych oraz komunikaty zwrotne dla webservices

	Args:
		serializers (serializers.ModelSerializer): Serializer oparty na modelu danych
	"""
	oldPassword = serializers.CharField(required=False) # stare hasło
	class Meta:
		model = User
		fields = ('password', 'oldPassword')
		extra_kwargs = {
            'password': {'write_only': True},
            'oldPassword': {'write_only': True}
        }