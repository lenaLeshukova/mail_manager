from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import logging
from .models import Log
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from mailing.models import Mailing, Log

logger = logging.getLogger(__name__)


def send_mailing_messages(mailing):
    """Функция отправки писем для конкретной рассылки."""
    now = timezone.now()

    # Инициация: Проверка временного диапазона
    if not (mailing.start_time <= now <= mailing.end_time):
        print(
            f"Ошибка: Рассылка #{mailing.id} не может быть запущена вне заданного времени!")
        return False

    if not mailing.is_active:
        print(f"Ошибка: Рассылка #{mailing.id} отключена менеджером!")
        return False

    # Определение получателей и отправка писем
    for client in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False
            )
            # Успешный лог
            Log.objects.create(
                status='Успешно',
                server_response='Письмо успешно выведено в консоль разработчика.',
                mailing=mailing
            )
            print(f"Лог: Письмо для {client.email} успешно отправлено.")

        except Exception as e:
            # Лог с ошибкой
            Log.objects.create(
                status='Не успешно',
                server_response=str(e),
                mailing=mailing
            )
            print(f"Лог: Ошибка отправки для {client.email}: {e}")

    # Динамически пересчитываем статус после отправки
    mailing.update_status()
    return True
