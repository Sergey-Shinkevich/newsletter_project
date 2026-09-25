from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailing.forms import ClientForm, MailingForm, MessageForm
from mailing.models import Client, Mailing, MailingAttempt, Message
from mailing.services import send_mailing
from users.services import is_manager

# CLIENT VIEWS


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Client.objects.all()  # Менеджер видит всех клиентов
        return Client.objects.filter(owner=user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        client = form.save(commit=False)
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            # Менеджер не должен редактировать клиентов, блокируем доступ
            return Client.objects.none()
        return Client.objects.filter(owner=user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Client.objects.none()
        return Client.objects.filter(owner=user)


# MESSAGE VIEWS


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        message = form.save(commit=False)
        message.owner = self.request.user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Message.objects.none()
        return Message.objects.filter(owner=user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Message.objects.none()
        return Message.objects.filter(owner=user)


# MAILING VIEWS


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Mailing.objects.all()  # Менеджер видит все рассылки
        return Mailing.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user = self.request.user

        # 1. Формируем уникальный ключ кэша в зависимости от роли и ID пользователя
        if is_manager(user) or user.is_superuser:
            cache_key = "dashboard_stats_manager"
        else:
            cache_key = f"dashboard_stats_user_{user.pk}"

        # 2. Пытаемся достать готовый словарь метрик из Redis
        stats = cache.get(cache_key)

        # 3. Если в кэше ничего нет — считаем через запросы к БД
        if stats is None:
            if is_manager(user) or user.is_superuser:
                # Для менеджера показываем общую статистику по всей системе
                stats = {
                    "total_mailings": Mailing.objects.count(),
                    "active_mailings": Mailing.objects.filter(
                        status=Mailing.STATUS_RUNNING, start_datetime__lte=now, end_datetime__gte=now
                    ).count(),
                    "total_clients": Client.objects.count(),
                    "success_attempts": MailingAttempt.objects.filter(status=MailingAttempt.STATUS_SUCCESS).count(),
                    "failed_attempts": MailingAttempt.objects.filter(status=MailingAttempt.STATUS_FAILED).count(),
                }
            else:
                # Метрики для обычного владельца
                user_mailings = Mailing.objects.filter(owner=user)
                stats = {
                    "total_mailings": user_mailings.count(),
                    "active_mailings": user_mailings.filter(
                        owner=user, status=Mailing.STATUS_RUNNING, start_datetime__lte=now, end_datetime__gte=now
                    ).count(),
                    "total_clients": Client.objects.filter(owner=user).count(),
                    "success_attempts": MailingAttempt.objects.filter(
                        mailing__in=user_mailings, status=MailingAttempt.STATUS_SUCCESS
                    ).count(),
                    "failed_attempts": MailingAttempt.objects.filter(
                        mailing__in=user_mailings, status=MailingAttempt.STATUS_FAILED
                    ).count(),
                }

            # Сохраняем вычисленный словарь в Redis на 5 минут (300 секунд)
            cache.set(cache_key, stats, 300)

        # 4. Переносим все метрики из словаря кэша в контекст шаблона
        context.update(stats)
        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            # Менеджер может редактировать (например, отключать) любую рассылку
            return Mailing.objects.all()
        # Обычный пользователь — только свои
        return Mailing.objects.filter(owner=user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            # Менеджеру запрещено удалять рассылки по ТЗ
            return Mailing.objects.none()
        return Mailing.objects.filter(owner=user)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_list.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=user)


class MailingAttemptDetailView(LoginRequiredMixin, DetailView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_detail.html"

    def get_queryset(self):
        user = self.request.user
        if is_manager(user) or user.is_superuser:
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=user)


class RunMailingView(LoginRequiredMixin, View):
    """
    Представление для ручного запуска рассылки через POST-запрос из интерфейса.
    """

    def post(self, request, pk):
        user = request.user
        if is_manager(user) or user.is_superuser:
            mailing = get_object_or_404(Mailing, pk=pk)
        else:
            mailing = get_object_or_404(Mailing, pk=pk, owner=user)

        try:
            send_mailing(mailing)
            messages.success(request, "Рассылка успешно запущена и обработана!")
        except Exception as e:
            messages.error(request, f"Ошибка при запуске рассылки: {e}")

        return redirect("mailing:mailing_detail", pk=mailing.pk)
