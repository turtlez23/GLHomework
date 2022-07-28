from django.db import models
from django.contrib.auth.models import User

class AddressEntryManager(models.Manager):
  """Address book manager
  """
  pass


class AddressEntry(models.Model):
  """Address book model
  """
  name = models.CharField(max_length=100)
  lastname = models.CharField(max_length=100)
  middlename = models.CharField(max_length=100, null=True, blank=True)
  nickname = models.CharField(max_length=100, null=True, blank=True)

  phone = models.CharField(max_length=20, null=True, blank=True)
  mobile_phone = models.CharField(max_length=20, null=True, blank=True)
  email = models.EmailField(null=True, blank=True)
  
  company = models.TextField(max_length=500, null=True, blank=True)
  position = models.CharField(max_length=255, null=True, blank=True)

  added_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)

  objects = AddressEntryManager()

  def __str__(self):
    return f'{self.pk} {self.name} {self.lastname} {self.email} {self.company}'


class FavouriteEntryManager(models.Manager):
  """Favourite book manager
  """
  def check_unique(self):
    pass


class FavouriteEntry(models.Model):
  """Favourite book model
  """
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  address_book = models.ForeignKey(AddressEntry, on_delete=models.PROTECT)

  objects = FavouriteEntryManager()

  def __str__(self):
    return f'{self.user} - {self.address_book}'