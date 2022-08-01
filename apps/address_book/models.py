from django.db import models
from django.contrib.auth.models import User


class AddressEntryManager(models.Manager):
  """Address book manager
  """
  pass


class AddressEntry(models.Model):
  """Address book model
  """
  PUBLIC_SHARE = 'public'
  PRIVATE_SHARE = 'private'
  SHARE_CHOICES = [
    (PUBLIC_SHARE, PUBLIC_SHARE),
    (PRIVATE_SHARE, PRIVATE_SHARE),
  ]

  name = models.CharField(max_length=100)
  lastname = models.CharField(max_length=100)
  middlename = models.CharField(max_length=100, null=True, blank=True)
  nickname = models.CharField(max_length=100, null=True, blank=True)

  phone = models.CharField(max_length=20, null=True, blank=True)
  mobile_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='mobile phone')
  email = models.EmailField(null=True, blank=True)
  
  company = models.TextField(max_length=500, null=True, blank=True)
  position = models.CharField(max_length=255, null=True, blank=True)

  share = models.CharField(max_length=100, null=True, blank=True, choices=SHARE_CHOICES)

  user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name='owner')

  objects = AddressEntryManager()

  def __str__(self):
    return f'{self.pk} {self.name} {self.lastname} {self.email} {self.company}'


class FavouriteEntryManager(models.Manager):
  """Favourite book manager
  """
  pass


class FavouriteEntry(models.Model):
  """Favourite book model
  """
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  address_entry = models.ForeignKey(AddressEntry, on_delete=models.PROTECT, verbose_name='address entry')

  objects = FavouriteEntryManager()

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['user', 'address_entry'], name='unique_user_address_entry')
    ]

  def __str__(self):
    return f'{self.user} - {self.address_entry}'