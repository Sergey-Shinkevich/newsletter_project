from django.core.management.base import BaseCommand

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = "Запуск рассылок вручную через консоль"

    def handle(self, *args, **options):
        # Находим рассылки, которые созданы или запущены
        mailings = Mailing.objects.filter(status__in=[Mailing.STATUS_CREATED, Mailing.STATUS_RUNNING])

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет активных рассылок для запуска."))
            return

        for mailing in mailings:
            self.stdout.write(f"Запуск рассылки №{mailing.pk}...")
            send_mailing(mailing)
            self.stdout.write(self.style.SUCCESS(f"Рассылка №{mailing.pk} обработана."))
