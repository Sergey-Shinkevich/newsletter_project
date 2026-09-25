from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from users.forms import UserLoginForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("mailing.urls")),
    path("users/", include("users.urls", namespace="users")),
]
