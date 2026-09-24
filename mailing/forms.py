from django import forms
from mailing.models import Client, Mailing, Message


class StyleFormMixin:
    """Миксин для автоматического добавления Bootstrap-стилей к полям формы"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                existing_classes = field.widget.attrs.get("class", "")
                if "form-control" not in existing_classes and "form-select" not in existing_classes:
                    field.widget.attrs.update({"class": "form-control"})


class ClientForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ("email", "first_name", "last_name", "patronymic", "comment")


class MessageForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ("subject", "body")


class MailingForm(StyleFormMixin, forms.ModelForm):
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