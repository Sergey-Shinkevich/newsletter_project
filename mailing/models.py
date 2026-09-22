from django.conf import settings
from django.db import models


class Client(models.Model):
    email = models.EmailField(verbose_name="Email")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=150, blank=True, null=True, verbose_name="Отчество")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    # Внешний ключ на владельца (модель CustomUser)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="clients"
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        # Уникальность пары email и владелец
        unique_together = ("email", "owner")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    # Внешний ключ на владельца (модель CustomUser)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="messages"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


from django.utils import timezone


class Mailing(models.Model):
    STATUS_CREATED = "Создано"
    STATUS_RUNNING = "Запущено"
    STATUS_COMPLETED = "Завершено"

    STATUS_CHOICES = [(STATUS_CREATED, "Создано"), (STATUS_RUNNING, "Запущено"), (STATUS_COMPLETED, "Завершено"),]
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания рассылки")
    start_datetime = models.DateTimeField(verbose_name="Дата и время начала рассылки")
    end_datetime = models.DateTimeField(verbose_name="Дата и время окончания рассылки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED, verbose_name="Статус")

    # Внешний ключ на сообщение
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="mailings")

    # Связь многие ко многим с клиентами
    clients = models.ManyToManyField(Client, verbose_name="Получатели", related_name="mailings")

    # Внешний ключ на владельца
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", related_name="mailings")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка №{self.id} ({self.status})"


class MailingAttempt(models.Model):
    STATUS_SUCCESS = "Успешно"
    STATUS_FAILED = "Не успешно"

    STATUS_CHOICES = [(STATUS_SUCCESS, "Успешно"), (STATUS_FAILED, "Не успешно"),]

    attempt_datetime = models.DateTimeField(default=timezone.now, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус попытки")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ почтового сервера")

    # Внешний ключ на рассылку
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="attempts")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"

    def __str__(self):
        return f"Попытка {self.status} от {self.attempt_datetime.strftime('%Y-%m-%d %H:%M')}"
