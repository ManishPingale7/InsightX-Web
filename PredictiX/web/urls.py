from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="Home"),
    path("predict",views.predict,name="Predict"),
    path("predictions",views.predictions,name="Predictions"),
    path("explore",views.explore,name="Explore"),
    path("about", views.about, name="About"),
    
    path("login",views.login_user,name="Login"),
    path("signup",views.signup_user,name="Signup"),
    path("logout",views.logout_user,name="Logout"),
]
