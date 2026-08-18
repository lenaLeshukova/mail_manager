import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from mailing.models import Mailing
from mailing.services import send_mailing_messages

logger = logging.getLogger(__name__)

def check_and_send_mailings():
    print("Вызов задачи: Проверка активных периодических рассылок...")
    logger.info("Проверка активных периодических рассылок...")
    active_mailings = Mailing.objects.filter(status='Запущена', is_active=True)
    for mailing in active_mailings:
        send_mailing_messages(mailing)

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Исправлено: убрано лишнее подчёркивание в add_job
        scheduler.add_job(
            check_and_send_mailings,
            trigger=CronTrigger(minute="*/5"),  # Каждые 5 минут
            id="check_and_send_mailings",
            max_instances=1,
            replace_existing=True,
        )

        try:
            print("Планировщик рассылок успешно запущен!")
            logger.info("Старт планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            print("Планировщик остановлен.")
            scheduler.shutdown()

