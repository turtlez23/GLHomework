"""Logger module
"""
import datetime
import traceback

from abc import ABC, abstractmethod

from django.conf import settings
from django.db import connection
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class AbstractLogger(ABC):
  """Abstract logger with constant params
  """
  ERROR_MSG = 'error'
  WARNING_MSG = 'warning'
  INFO_MSG = 'info'
  DEBUG_MSG = 'debug'

  SYSTEM_LOG_TYPE = 'system'
  DB_LOG_TYPE = 'db'
  API_LOG_TYPE = 'api'

  @abstractmethod
  def log_message(cls, message:str, user:User, log_type:str, message_type:str):
    pass

class AddressBookSystemLogger(AbstractLogger):
  """Logger for saving system errors to file
  """
  name = 'Address Book'
  file_name = 'address_book_system.log'

  @classmethod
  def log_message(cls, message, user=None, log_type=AbstractLogger.SYSTEM_LOG_TYPE, message_type=AbstractLogger.ERROR_MSG):
    with open(settings.LOGS_DIRECTORY_PATH.joinpath(cls.file_name), 'a') as log_file:
      date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
      log_file.write(f"\n{date}, {log_type}, {message_type}, {message}{'; User {user}' if user else '' }")


class AddressBookSqlLogger(AbstractLogger):
  """Logger for saving sql statements to file
  """
  name = 'Address Book'
  file_name = 'address_book_sql_statements.log'

  @classmethod
  def log_message(cls, message, user=None):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
    with open(settings.LOGS_DIRECTORY_PATH.joinpath(cls.file_name), 'a+') as log_file:
      log_file.write(f"\n{date}, {message}{', User {user}' if user else '' }")

class AbstractLogsMiddleware(ABC):
  """Abstract middleware
  """
  def _log_sql_statements_message(self, message:str, user:User=None):
    """Log sql statements

    Args:
        message (str): _description_
        user (User, optional): django user. Defaults to None.
    """
    AddressBookSqlLogger.log_message(message, user)
  
  def _log_error_message(self, message, user=None):
    """Log system error statements

    Args:
        message (str): _description_
        user (User, optional): django user. Defaults to None.
    """
    AddressBookSystemLogger.log_message(message, user)

  def _create_error_response(self, data:dict, status:status)->Response:
    """Create http response

    Args:
        data (dict): response data
        status (status): http status for example status.HTTP_500_INTERNAL_SERVER_ERROR

    Returns:
        Response: json http response
    """
    response = Response(data=data, status=status)
    response.accepted_renderer = JSONRenderer()
    response.renderer_context = {}
    response.accepted_media_type = "application/json"
    response.render()
    return response


class SqlLogsMiddleware(AbstractLogsMiddleware):
  """Middleware for register sql statements in file
  """
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)
    # skip static files
    if not settings.DEBUG or len(connection.queries) == 0 or\
      request.path_info.startswith(settings.MEDIA_URL) or \
      request.path_info.startswith(settings.STATIC_URL) or \
      '/admin/jsi18n/' in request.path_info:
      return response

    try:
      self._log_sql_statements_message(f"[SQL Queries for]: {request.path_info}, {request.user}")
      total_time = 0.0
      for query in connection.queries:
          nice_sql = query['sql'].replace('"', '').replace(',', ', ')
          total_time += float(query['time'])
          self._log_sql_statements_message(f"[{query['time']}] {nice_sql}")
      self._log_sql_statements_message(f"[TOTAL TIME]: {str(total_time)} seconds, [TOTAL QUERIES]: {len(connection.queries)}")

    except Exception:
      self._log_error_message(f"AddressBookSqlLogger error: {traceback.format_exc()}", request.user)
      response = self._create_error_response({"detail":"AddressBookSqlLogger error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


class ErrorLogsMiddleware(AbstractLogsMiddleware):
  """Middleware for register errors in file
  """
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    return self.get_response(request)
  
  def process_exception(self, request, exception):
    """Method for processing all raised exceptions
    """
    AddressBookSystemLogger.log_message(f"AddressBookSqlLogger error: {traceback.format_exc()}", request.user)
        
    return self._create_error_response({"detail":"Internal server error contact with administrator"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
