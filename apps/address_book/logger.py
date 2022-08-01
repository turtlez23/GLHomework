from django.conf import settings
import datetime

class Logger():
  ERROR_MSG = 'error'
  WARNING_MSG = 'warning'
  INFO_MSG = 'info'
  DEBUG_MSG = 'debug'

  SYSTEM_LOG_TYPE = 'system'
  DB_LOG_TYPE = 'db'
  API_LOG_TYPE = 'api'


class AddressBookLogger(Logger):
  name = 'Address Book'
  file_name = 'address_book'

  @classmethod
  def log_message(cls, message, user, log_type=Logger.SYSTEM_LOG_TYPE, message_type=Logger.INFO_MSG):
    with open(settings.LOGS_DIRECTORY_PATH.joinpath(cls.file_name), 'a') as log_file:
      date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')
      log_file.write(f'{date}, {log_type}, {message_type}, {message}, User {user}')
