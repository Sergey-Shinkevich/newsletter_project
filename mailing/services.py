from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from mailing.models import Mailing, MailingAttempt


def send_mailing(mailing: Mailing):
    """
    Функция отправки рассылки: проверяет временной интервал, отправляет письма клиентам и сохраняет попытку отправки.
    """
    current_time = datetime.now()

    # Проверяем, находится ли текущее время в пределах запланированного интервала или статус рассылки позволяет отправку
    if mailing.start_datetime <= current_time <= mailing.end_datetime:
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save()

        # Получаем всех клиентов, привязанных к этой рассылке
        clients = mailing.clients.all()

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

                # Фиксируем успешную попытку
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status=MailingAttempt.STATUS_SUCCESS,
                    server_response=str(response)
                )
            except Exception as e:
                # Фиксируем неудачную попытку и сохраняем ошибку
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status=MailingAttempt.STATUS_FAILED,
                    server_response=str(e)
                )

        # После завершения итерации по клиентам меняем статус рассылки на завершенную
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save()