from django.utils import timezone
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from mailing.services import send_mailing
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from mailing.forms import ClientForm, MessageForm, MailingForm
from mailing.models import Client, Message, Mailing, MailingAttempt


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"

    def get_queryset(self):
        # Пользователь видит только своих клиентов
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        client = form.save(commit=False)
        client.owner = self.request.user  # Привязываем клиента к текущему владельцу
        client.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


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
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)





class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user = self.request.user

        # Метрики
        context["total_mailings"] = Mailing.objects.filter(owner=user).count()
        context["active_mailings"] = Mailing.objects.filter(
            owner=user,
            status=Mailing.STATUS_RUNNING,
            start_datetime__lte=now,
            end_datetime__gte=now
        ).count()
        context["total_clients"] = Client.objects.filter(owner=user).count()

        # Статистика попыток по рассылкам текущего пользователя
        user_mailings = Mailing.objects.filter(owner=user)
        context["success_attempts"] = MailingAttempt.objects.filter(
            mailing__in=user_mailings,
            status=MailingAttempt.STATUS_SUCCESS
        ).count()
        context["failed_attempts"] = MailingAttempt.objects.filter(
            mailing__in=user_mailings,
            status=MailingAttempt.STATUS_FAILED
        ).count()

        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Передаем текущего пользователя в форму
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
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_list.html"

    def get_queryset(self):
        # Показываем попытки только для рассылок текущего пользователя
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)


class MailingAttemptDetailView(LoginRequiredMixin, DetailView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempt_detail.html"

    def get_queryset(self):
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)



class RunMailingView(LoginRequiredMixin, View):
    """
    Представление для ручного запуска рассылки через POST-запрос из интерфейса.
    """

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

        try:
            send_mailing(mailing)
            messages.success(request, "Рассылка успешно запущена и обработана!")
        except Exception as e:
            messages.error(request, f"Ошибка при запуске рассылки: {e}")

        return redirect("mailing:mailing_detail", pk=mailing.pk)