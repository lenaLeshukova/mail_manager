import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from mailing.models import Log

logger = logging.getLogger(__name__)


def send_mailing_messages(mailing):
    """Функция отправки писем для конкретной рассылки с batch-сохранением логов."""
    now = timezone.now()

    # Инициация: Проверка временного диапазона по ТЗ
    if not (mailing.start_time <= now <= mailing.end_time):
        print(f"Ошибка: Рассылка #{mailing.id} не может быть запущена вне заданного времени!")
        return False

    if not mailing.is_active:
        print(f"Ошибка: Рассылка #{mailing.id} отключена менеджером!")
        return False

    # Список для пакетного сбора логов в оперативной памяти (batch)
    logs_to_create = []

    # Определение получателей и отправка писем каждому в цикле
    for client in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False
            )
            # Не пишем в БД сразу, а просто добавляем объект лога в список
            logs_to_create.append(Log(
                status='Успешно',
                server_response='Письмо успешно выведено в консоль разработчика.',
                mailing=mailing
            ))
            print(f"Лог: Письмо для {client.email} успешно отправлено.")

        except Exception as e:
            # Если отправка упала — добавляем лог ошибки в список
            logs_to_create.append(Log(
                status='Не успешно',
                server_response=str(e),
                mailing=mailing
            ))
            print(f"Лог: Ошибка отправки для {client.email}: {e}")

    # Сохранение логов в БД происходит через пакетный запрос (batch)
    if logs_to_create:
        Log.objects.bulk_create(logs_to_create, batch_size=500)
        print(f"Пакетная запись (batch) из {len(logs_to_create)} логов успешно сохранена в БД.")

    # Динамически пересчитываем статус после отправки
    mailing.update_status()
    return True
