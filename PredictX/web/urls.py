from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="Home"),
    path("predict",views.predict,name="Predict"),
    path("diagnose",views.diagnose,name="Diagnose"),
    path("history",views.history,name="History"),
    path("explore",views.explore,name="Explore"),
    path("bearing", views.monitoring, name="Monitoring"),
    path("delete-record/<int:id>", views.delete_record, name="Delete"),
    path("dashboard/<int:id>",views.dashboard,name="Dashboard"),
    path("condition/<int:id>",views.condition,name="Condition"),

    path("login",views.login_user,name="Login"),
    path("signup",views.signup_user,name="Signup"),
    path("logout",views.logout_user,name="Logout"),

    path('vibration-analysis/', views.vibration_analysis,
         name='vibration_analysis'),
    # Optional: Add a URL to view past reports
    path('vibration-reports/', views.vibration_reports, name='vibration_reports'),
    path('download-report/<int:record_id>/',
         views.download_vibration_report, name='download_vibration_report'),
]
