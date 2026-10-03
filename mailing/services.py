from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from mailing.models import Mailing, MailingAttempt


def send_mailing(mailing: Mailing):
    """
    Функция отправки рассылки: отправляет письма клиентам и сохраняет попытки пачкой (batch / bulk_create).
    """
    current_time = timezone.now()

    if mailing.status in [Mailing.STATUS_CREATED, Mailing.STATUS_RUNNING]:
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save()

        clients = mailing.clients.all()

        if not clients:
            raise Exception("К этой рассылке не привязано ни одного клиента!")

        attempts_to_create = []

        for client in clients:
            try:
                # Отправляем email
                response = send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email],
                    fail_silently=False,
                )

                # Добавляем успешную попытку в список для пакетного создания
                attempts_to_create.append(
                    MailingAttempt(
                        mailing=mailing, status=MailingAttempt.STATUS_SUCCESS, server_response=str(response)
                    )
                )
            except Exception as e:
                # Добавляем неудачную попытку в список для пакетного создания
                attempts_to_create.append(
                    MailingAttempt(mailing=mailing, status=MailingAttempt.STATUS_FAILED, server_response=str(e))
                )

        # Сохраняем все попытки в базу данных одним запросом (batch / bulk_create)
        if attempts_to_create:
            MailingAttempt.objects.bulk_create(attempts_to_create)

        # Меняем статус рассылки на завершенный
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save()
    else:
        raise Exception(f"Рассылка имеет статус '{mailing.get_status_display()}' и не может быть запущена.")
