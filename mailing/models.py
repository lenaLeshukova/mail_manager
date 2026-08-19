from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    comment = models.TextField(blank=True, null=True,
                               verbose_name='Комментарий')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              verbose_name='Владелец')

    def __str__(self):
        return self.full_name


class Message(models.Model):
    title = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              verbose_name='Владелец')

    def __str__(self):
        return self.title


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='Создана', verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE,
                                verbose_name='Сообщение')
    recipients = models.ManyToManyField(Client, verbose_name='Получатели')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              verbose_name='Владелец')
    is_active = models.BooleanField(default=True,
                                    verbose_name='Активна (доступна для отправки)')

    def clean(self):
        # Валидация дат
        if self.start_time and self.start_time < timezone.now() and not self.pk:
            raise ValidationError('Дата начала не может быть в прошлом.')
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                'Дата начала должна быть раньше даты окончания.')

    def update_status(self):
        now = timezone.now()
        new_status = self.status

        if now < self.start_time:
            new_status = 'Создана'
        elif self.start_time <= now <= self.end_time:
            new_status = 'Запущена'
        elif now > self.end_time:
            new_status = 'Завершена'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Рассылка {self.id} ({self.status})"


class Log(models.Model):
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]
    attempt_time = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              verbose_name='Статус')
    server_response = models.TextField(blank=True, null=True,
                                       verbose_name='Ответ сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE,
                                verbose_name='Рассылка')

    def __str__(self):
        return f"Попытка {self.id} - {self.status}"
