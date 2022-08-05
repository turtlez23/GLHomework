Address book application

The application has only a backend. I've implemented an address book API for logged users and a Django admin page for administrators or users in which staff status is True.
Django, Django Rest Framework was used to build an application and SQLite for persisting data.
You can run this application using Django dev server. Also, I’ve prepared a Postman requests collection with which you can test features.


1) Features:

* Django admin CMS:
  - with standard user and groups pages
  - CRUD for address and favorite entries

* User API based on Django Rest Framework
  AddressEntry:
  - Add contacts to address book
  - You can make address entry PRIVATE or PUBLIC
  - Edit contacts when you are an owner
  - Only owner can change address entry
  - Remove and add contact to favorites when you add or edit them
  - Remove contacts from address book with favorites, when contact is PUBLIC then it has no owner, only admin can change this
 
  FavoriteEntry
  - Get contacts when you are an owner and contacts are PUBLIC
  - Tag many contacts as favorite at the same time
  - Remove favorite only if you are owner
  - Edit favorites
 
  User
  - Show personal data
  - Edit personal data
  - Change password

* Basic and Session authentication
* Error handling with logging to file using Middleware class
* Log all SQL statements with basic time counter to file using Middleware class

* Swagger API documentation


2) Main URLs:
- http://127.0.0.1:8000/ - main page
- http://127.0.0.1:8000/admin - admin page
- http://127.0.0.1:8000/about - about page
- http://127.0.0.1:8000/api/rest/v1/ - clients api
- http://127.0.0.1:8000/api/rest/v1/docs - swagger documentation


3) Postman API collection:
filepath - /docs/AddressBook.postman_collection


4) How to run developer environment:
- python3 pip install -r requirements
- python3 manage.py createsuperuser
- python3 manage.py migrate
- python3 manage.py makemigrations address_book
- python3 manage.py migrate address_book
- python3 manage.py collectstatic
- python3 manage.py runserver 0.0.0.0:8000
