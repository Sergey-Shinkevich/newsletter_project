from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from mailing.apps import MailingConfig
from mailing.views import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    MailingAttemptDetailView,
    MailingAttemptListView,
    RunMailingView,
)
from users.forms import UserLoginForm

app_name = MailingConfig.name

urlpatterns = [
    # Клиенты
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),

    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),

    # Рассылки
    path("", MailingListView.as_view(), name="mailing_list"),  # Главная страница приложения - список рассылок
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),

    # Попытка рассылки (логи)
    path("attempts/", MailingAttemptListView.as_view(), name="attempt_list"),
    path("attempts/<int:pk>/", MailingAttemptDetailView.as_view(), name="attempt_detail"),

    # Запуск рассылки
    path("mailings/<int:pk>/run/", RunMailingView.as_view(), name="run_mailing"),

    path('accounts/login/', LoginView.as_view(
        template_name='mailing/mailing_form.html',
        authentication_form=UserLoginForm,
        extra_context={"button_text": "Войти"}  # <--- Вот эта строчка сделает кнопку "Войти"
    ), name='login'),

    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]



