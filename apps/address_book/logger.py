import datetime
import traceback

from django.conf import settings
from django.db import connection

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class Logger:
  ERROR_MSG = 'error'
  WARNING_MSG = 'warning'
  INFO_MSG = 'info'
  DEBUG_MSG = 'debug'

  SYSTEM_LOG_TYPE = 'system'
  DB_LOG_TYPE = 'db'
  API_LOG_TYPE = 'api'


class AddressBookSystemLogger(Logger):
  name = 'Address Book'
  file_name = 'address_book_system.log'

  @classmethod
  def log_message(cls, message, user=None, log_type=Logger.SYSTEM_LOG_TYPE, message_type=Logger.ERROR_MSG):
    with open(settings.LOGS_DIRECTORY_PATH.joinpath(cls.file_name), 'a') as log_file:
      date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
      log_file.write(f"\n{date}, {log_type}, {message_type}, {message}{'; User {user}' if user else '' }")


class AddressBookSqlLogger(Logger):
  name = 'Address Book'
  file_name = 'address_book_sql_statements.log'

  @classmethod
  def log_message(cls, message, user=None):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
    with open(settings.LOGS_DIRECTORY_PATH.joinpath(cls.file_name), 'a+') as log_file:
      log_file.write(f"\n{date}, {message}{', User {user}' if user else '' }")

class LogsMiddleware:

  def _log_sql_statements_message(self, message, user=None):
    AddressBookSqlLogger.log_message(message, user)
  
  def _log_error_message(self, message, user=None):
    AddressBookSystemLogger.log_message(message, user)

  def _create_error_response(self, data, status):
    response = Response(data=data, status=status)
    response.accepted_renderer = JSONRenderer()
    response.renderer_context = {}
    response.accepted_media_type = "application/json"
    response.render()
    return response


class SqlLogsMiddleware(LogsMiddleware):

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)
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


class ErrorLogsMiddleware(LogsMiddleware):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    return self.get_response(request)
  
  def process_exception(self, request, exception):
    AddressBookSystemLogger.log_message(f"AddressBookSqlLogger error: {traceback.format_exc()}", request.user)
        
    return self._create_error_response({"detail":"Internal server error contact with administrator"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
