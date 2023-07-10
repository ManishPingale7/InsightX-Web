from . import views
from django.urls import path

urlpatterns = [
    path("login",views.login_user),
    path("signup",views.signup_user),
    path("predict",views.predict),
    path("predictions",views.predictions),
]
