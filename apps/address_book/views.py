"""Address book application views
"""

from typing import Dict, Any

from django.conf import settings
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.transaction import atomic
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, BaseFilterBackend

from apps.address_book.models import AddressEntry, FavoriteEntry
from apps.address_book.serializers import AddressEntrySerializer, FavoriteEntrySerializer, UserDataSerializer, PasswordSerializer


def home_page(request):
  """Home page view implemented by method with request

  Args:
      request (HttpRequest): http request

  Returns:
      HttpResponse: http response
  """
  return render(request, "address_book/home.html", {'title': settings.ADDRESS_BOOK_TITLE})

class AuthentificatedModelViewSet(ModelViewSet):
  """ModelViev set with authentificaton and permission configuration
  """
  authentication_classes = [SessionAuthentication, BasicAuthentication]
  permission_classes = [IsAuthenticated]

class AboutView(TemplateView):
  """Abaut page view implemented by TemplateView
  """
  template_name = "address_book/about.html"

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    return {'title': settings.ABOUT_PAGE_TITLE}


class IsUserFilterBackend(BaseFilterBackend):
  """
  Filter that only allows users to see their own objects
  """
  def filter_queryset(self, request, queryset, view):
      return queryset.filter(user=request.user)


class IsAddressAllowedFilterBackend(IsUserFilterBackend):
  """
  Filter that only allows users to see their own objects 
  or address entry which has no owner if the entry has to be a public
  """
  def filter_queryset(self, request, queryset, view):
      return queryset.filter(Q(user=request.user) | Q(share=AddressEntry.PUBLIC_SHARE))


class AddressEntryViewSet(AuthentificatedModelViewSet):
  """Views for address entry
  """
  queryset = AddressEntry.objects.all()
  serializer_class = AddressEntrySerializer
  http_method_names = ['head', 'get', 'post', 'put', 'delete']
  filter_backends = [DjangoFilterBackend, OrderingFilter, IsAddressAllowedFilterBackend]
  ordering = ['name']
  ordering_fields = ['id', 'name', 'lastname']
  filterset_fields = ['name', 'lastname', 'middlename', 'nickname', 'phone', 'mobile_phone', 'email', 'company', 'position']

  def get_bad_owner_request(self):
    """Get request when objects does not belong to the current user

    Returns:
        Response: http response
    """
    return Response({
        "user": [
            "You cannot change other user address entry"
        ]
    }, status=status.HTTP_400_BAD_REQUEST)
  
  def check_owner(self, request):
    """Check owner

    Args:
        request (Request): http request

    Returns:
        bool: True if object belong to user
    """
    return request.data.get("user") !=  request.user.pk
  
  def add_to_favorites(self, user, address_entry_id):
    FavoriteEntry(user=user, address_entry=AddressEntry(id=address_entry_id)).save()

  def update_favorite_entry(self, request, address_entry_id):
    """Update favorite entry
    add_to_favorite is True and favorite exist doing nothing
    add_to_favorite is True and favorite didn't exist add to favorite
    add_to_favorite is False and favorite exist delete favorite entry
    add_to_favorite is False and favorite didn't exist doing nothing
    
    Args:
        request (Request): http request
        address_entry_id (int): address entry id
    """
    favoriteEntry = FavoriteEntry.objects.filter(user=request.user, address_entry=address_entry_id).first()
    if request.data.get("add_to_favorite"):
      if not favoriteEntry:
        FavoriteEntry(user=request.user, address_entry=AddressEntry(id=address_entry_id)).save()
    elif favoriteEntry:
      favoriteEntry.delete()


  @atomic
  def create(self, request, *args, **kwargs):
    """Save object to db and if add_to_favorite param is true than method adding address entry to favorite table, using logged user and id from saved entry object

    Returns:
        Response: Http response
    """
    if self.check_owner(request):
      return self.get_bad_owner_request()

    response = super().create(request, *args, **kwargs)

    # check favorite entries
    if request.data.get("add_to_favorite"):
      self.add_to_favorites(request.user, response.data.get("id"))
    return response

  @atomic
  def update(self, request, *args, **kwargs):
    """Update object,
    add_to_favorite param is true - method adding address entry to favorite table if not exist,
    add_to_favorite is equal false - method delete entry from favorite if exist

    Returns:
        Response: Http response
    """
    if self.check_owner(request):
      return self.get_bad_owner_request()

    response = super().update(request, *args, **kwargs)
    
    self.update_favorite_entry(request, response.data.get("id"))

    return response

  @atomic
  def destroy(self, request, *args, **kwargs):
    """Destroy address entry and favorite entries
    address entry is public - change user to null and delete current user favorite entry
    address entry is private - delete favorite entry
    next delete object

    Args:
        request (Request): http request

    Returns:
        Response: http response
    """
    instance = self.get_object()
    if instance.share == AddressEntry.PUBLIC_SHARE:
      # change object owner
      instance.update(user=None)
      # delete entries for current user
      FavoriteEntry.objects.filter(user=request.user, address_entry=instance.pk).delete()

      return Response(status=status.HTTP_204_NO_CONTENT)

    # delete all private entries
    FavoriteEntry.objects.filter(address_entry=instance.pk).delete()
    # delete address entry
    return super().destroy(request, *args, **kwargs)


class FavoriteEntryViewSet(AuthentificatedModelViewSet):
  """Views for favorite address entry
  """
  queryset = FavoriteEntry.objects.all().order_by('user__last_name')
  serializer_class = FavoriteEntrySerializer
  http_method_names = ['head', 'get', 'post', 'delete']
  filter_backends = [DjangoFilterBackend, IsUserFilterBackend]
  
  def get_queryset(self):
    f"""Method with optional filter for: address_entry

    Returns:
        QuerySet: query set with filters
    """
    address_entry = self.request.query_params.get('address_entry')
    if address_entry is not None:
      self.queryset = self.queryset.filter(address_entry=address_entry)
    return self.queryset



class UserDataViewSet(AuthentificatedModelViewSet):
  """User data view set for changing personal data and password
  """
  queryset = User.objects.all()
  serializer_class = UserDataSerializer
  http_method_names = ['head', 'get', 'put']

  def get_bad_owner_request(self):
    """Get request when objects does not belong to the current user

    Returns:
        Response: http response
    """
    return Response({
        "id": [
            "You cannot change other user data"
        ]
    }, status=status.HTTP_400_BAD_REQUEST)
  
  def check_owner(self, request):
    """Check owner

    Args:
        request (Request): http request

    Returns:
        bool: True if object belong to user
    """
    return request.data.get("id") !=  request.user.pk

  def list(self, request, *args, **kwargs):
    return Response({
      "detail": "Method \"GET\" for list not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

  def get_queryset(self):
    f"""Method with user_id filter for address_entry

    Returns:
        QuerySet: query set with filters
    """
    queryset = self.queryset.filter(id=self.request.user.pk)
    return queryset

  def check_old_password(self, request):
    return not request.user.check_password(request.data.get("old_password"))
    
  @action(detail=True, methods=['put'], url_name='password')  
  def password(self, request, pk):
    """Change current user password,
    User has to send old password for authentyfication 

    Args:
        request (HttpRequest): http request

    Returns:
        Response: odpowiedź w formacie Response(json)
    """
    user = request.user
    password = request.data.get("password")

    if self.check_old_password(request):
      return Response({'detail':'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
      validate_password(password, user)
    except ValidationError:
      return Response({'detail':'Password is not compatible with the security policy'}, status=status.HTTP_400_BAD_REQUEST)

    data = {"password": make_password(password)}
    serializer = PasswordSerializer(
      self.get_object(), data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({'detail':'The password has been changed'}, status=status.HTTP_200_OK)
