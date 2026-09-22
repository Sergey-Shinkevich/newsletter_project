from django import forms
from mailing.models import Client, Mailing, Message


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ("email", "first_name", "last_name", "patronymic", "comment")


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("subject", "body")


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ("start_datetime", "end_datetime", "message", "clients")
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Пользователь может выбирать только свои сообщения и своих клиентов
            self.fields["message"].queryset = Message.objects.filter(owner=self.user)
            self.fields["clients"].queryset = Client.objects.filter(owner=self.user)