from django.contrib import admin

from mailing.models import Client, Mailing, MailingAttempt, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "owner")
    list_filter = ("owner",)
    search_fields = ("email", "first_name", "last_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner")
    list_filter = ("owner",)
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "start_datetime", "end_datetime", "message", "owner")
    list_filter = ("status", "owner")
    search_fields = ("message__subject",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("attempt_datetime", "status", "mailing")
    list_filter = ("status",)
    search_fields = ("server_response",)
