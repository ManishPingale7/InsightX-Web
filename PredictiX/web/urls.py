from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="Home"),
    path("login",views.login_user,name="Login"),
    path("signup",views.signup_user,name="Signup"),
    path("logout",views.logout_user,name="Logout"),
    path("predict",views.predict,name="Predict"),
    path("predictions",views.predictions,name="Predictions"),
    path("plots",views.plots,name="Login"),
]
