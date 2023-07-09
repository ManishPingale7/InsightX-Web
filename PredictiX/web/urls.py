from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="Home"),
    path("login",views.loginUser,name="Login"),
    path("signup",views.signupUser,name="Signup"),
    path("logout",views.logoutUser,name="Logout"),
    path("predictions",views.predictions,name="Predictions"),
    path("get-token",views.get_csrf_token,name="Token"),
    path("predict",views.predict,name="Predict")
]
