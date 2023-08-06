from . import views
from django.urls import path

urlpatterns = [
    path("login", views.login_user),
    path("signup", views.signup_user),
    # path("predict",views.predict),
    path("records", views.all_records),
    path("records/<str:id>", views.single_record),
]

"""
GET records - all records : list of records
POST records - add record : single record

GET records/1 - get single record : single record
DELETE records/1 - delete single record : String response
"""
