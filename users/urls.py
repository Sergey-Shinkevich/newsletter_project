from django.contrib.auth.views import (LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)
from django.shortcuts import render
from django.urls import path, reverse_lazy
from users.apps import UsersConfig
from users.views import RegisterView, activate
from users.forms import UserLoginForm

app_name = UsersConfig.name

urlpatterns = [

    path("login/", LoginView.as_view(
        template_name="mailing/mailing_form.html",
        authentication_form=UserLoginForm
    ), name="login"),

    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("register/done/", lambda r: render(r, "users/register_done.html"), name="register_done"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),

    # Восстановление пароля
    path("password-reset/", PasswordResetView.as_view(template_name="users/password_reset_form.html",
                                                      email_template_name="users/password_reset_email.html",
                                                      success_url=reverse_lazy("users:password_reset_done")),
         name="password_reset"),
    path("password-reset/done/", PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html",
                                                                     success_url=reverse_lazy(
                                                                         "users:password_reset_complete")),
         name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name="password_reset_complete"),
]