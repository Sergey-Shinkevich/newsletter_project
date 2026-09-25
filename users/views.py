from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, ListView

from config import settings
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from users.services import is_manager
from users.tokens import account_activation_token


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        # Пользователь неактивен, пока не подтвердит почту
        user.is_active = False
        user.save()

        # Формируем ссылку для подтверждения email
        current_site = get_current_site(self.request)
        mail_subject = "Активация аккаунта в сервисе рассылок"
        message = render_to_string(
            "users/acc_active_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )

        # Отправляем письмо
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])
        return super().form_valid(form)


def activate(request, uidb64, token):
    """
    Функция активирует пользователя, если токен и uid валидны.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("mailing:mailing_list")  # Перенаправляем на главную страницу рассылок
    else:
        return render(request, "users/activate_invalid.html")


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users_list"

    def test_func(self):
        # Доступ только для менеджеров или суперпользователей
        return is_manager(self.request.user)


class ToggleUserStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Представление для блокировки/активации пользователя менеджером"""

    def test_func(self):
        return is_manager(self.request.user)

    def post(self, request, pk):
        user_to_toggle = get_object_or_404(CustomUser, pk=pk)

        # Защита от блокировки самого себя или суперпользователя
        if user_to_toggle == request.user or user_to_toggle.is_superuser:
            messages.error(request, "Нельзя заблокировать себя или суперпользователя!")
        else:
            # Меняем статус на противоположный
            user_to_toggle.is_active = not user_to_toggle.is_active
            user_to_toggle.save()
            status_msg = "разблокирован" if user_to_toggle.is_active else "заблокирован"
            messages.success(request, f"Пользователь {user_to_toggle.email} успешно {status_msg}.")

        return redirect("users:user_list")
