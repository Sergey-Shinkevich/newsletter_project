from django import forms
from mailing.models import Client, Message


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ("email", "first_name", "last_name", "patronymic", "comment")


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("subject", "body")