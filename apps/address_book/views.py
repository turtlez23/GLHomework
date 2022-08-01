from typing import Dict, Any

from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, BaseFilterBackend
from django_filters.rest_framework import DjangoFilterBackend

from apps.address_book.models import AddressEntry, FavouriteEntry
from apps.address_book.serializers import AddressEntrySerializer, FavouriteEntrySerializer, UserDataSerializer, PasswordSerializer

from django.db.transaction import atomic

from rest_framework import status
from django.db.models import Q

from django.contrib.auth.models import User
from rest_framework.decorators import action
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

def home_page(request):
  """Home page view implemented by method with request param

  Args:
      request (HttpRequest): http request

  Returns:
      HttpResponse: http response
  """
  return render(request, "address_book/home.html", {'title': settings.ADDRESS_BOOK_TITLE})

class AuthentificationModelViewSet(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

class AboutView(TemplateView):
  """Abaut page view implemented by TemplateView
  """
  template_name = "address_book/abaut.html"

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    return {'title': settings.ABOUT_PAGE_TITLE}


class IsUserFilterBackend(BaseFilterBackend):
  """
  Filter that only allows users to see their own objects.
  """
  def filter_queryset(self, request, queryset, view):
      return queryset.filter(user=request.user)


class IsAddressAllowedFilterBackend(IsUserFilterBackend):
  """
  Filter that only owner or address entry has no user but the entry has to be a public to see their own objects.
  """
  def filter_queryset(self, request, queryset, view):
      return queryset.filter(Q(user=request.user) | Q(share=AddressEntry.PUBLIC_SHARE))


class AddressEntryViewSet(AuthentificationModelViewSet):
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
    return Response({
        "user": [
            "You cannot change other user address entry"
        ]
    }, status=status.HTTP_400_BAD_REQUEST)

  @atomic
  def create(self, request, *args, **kwargs):
    """Save object to db and if add_to_favourite param is true method adding address entry to favouite using logged user and id from new address entry object

    Returns:
        Response: Http response
    """
    #sprawdzenie czy user jest właścicielem
    if request.data.get("user") !=  request.user.pk:
      return self.get_bad_owner_request()

    response = super().create(request, *args, **kwargs)

    # obsługa favourite
    if request.data.get("add_to_favourite"):
      FavouriteEntry(user=request.user, address_entry=AddressEntry(id=response.data.get("id"))).save()
    return response

  @atomic
  def update(self, request, *args, **kwargs):
    #sprawdzenie czy user jest właścicielem
    if request.data.get("user") !=  request.user.pk:
      return self.get_bad_owner_request()

    response = super().update(request, *args, **kwargs)
    
    # obsługa favourite
    favEntry = FavouriteEntry.objects.filter(user=request.user, address_entry=response.data.get("id")).first()
    if request.data.get("add_to_favourite"):
      if not favEntry:
        FavouriteEntry(user=request.user, address_entry=AddressEntry(id=response.data.get("id"))).save()
    elif favEntry:
      favEntry.delete()

    return response

  @atomic
  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.share == AddressEntry.PUBLIC_SHARE:
      instance.update(user=None)
      # delete entries for current user
      FavouriteEntry.objects.filter(user=request.user, address_entry=instance.pk).delete()

      return Response(status=status.HTTP_204_NO_CONTENT)

    # delete all private entries
    FavouriteEntry.objects.filter(address_entry=instance.pk).delete()

    return super().destroy(request, *args, **kwargs)

class FavouriteEntryViewSet(AuthentificationModelViewSet):
  """Views for favourite address entry
  """
  queryset = FavouriteEntry.objects.all().order_by('user__last_name')
  serializer_class = FavouriteEntrySerializer
  http_method_names = ['head', 'get', 'post', 'delete']
  filter_backends = [DjangoFilterBackend, IsUserFilterBackend]
  
  def get_queryset(self):
    f"""Method with optional filter for: address_entry

    Returns:
        QuerySet: query set with filters
    """
    address_entry = self.request.query_params.get('address_entry')
    if address_entry is not None:
      self.queryset.filter(address_entry=address_entry)
    return self.queryset


  class UserDataViewSet(AuthentificationModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDataSerializer
    http_method_names = ['head', 'get', 'put']

  def list(self, request, *args, **kwargs):
    return Response({
      "detail": "Method \"GET\" for list not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

  def get_queryset(self):
    f"""Method with optional filter for: address_entry

    Returns:
        QuerySet: query set with filters
    """
    self.queryset.get(id=self.request.user.pk)
    return self.queryset

    
  @action(detail=True, methods=['put'], url_name='password')  
  def password(self, request, pk):
    """Edycja hasła - id uzytkownika pobrane z request, nalezy podać stare hasło

    Args:
      request (HttpRequest): żądanie
    Returns:
      Response: odpowiedź w formacie Response(json)
    """
    user = request.user
    oldPassword = request.data.get("oldPassword")
    password = request.data.get("password")
    
    if not request.user.check_password(oldPassword):
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