from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Добавляем редирект с корня на список рассылок
    path("", lambda request: redirect("mailing:mailing_list"), name="home"),
    path("", include("mailing.urls")),
    path("users/", include("users.urls")),
]
