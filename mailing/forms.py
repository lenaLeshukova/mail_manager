from django import forms
from mailing.models import Mailing
from django import forms

from mailing.models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        # Перечисляем поля в нужном порядке
        fields = ['start_time', 'end_time', 'message', 'recipients']

        # Задаем красивые и понятные подписи для полей
        labels = {
            'start_time': 'Дата и время начала рассылки',
            'end_time': 'Дата и время окончания рассылки',
            'message': 'Текст сообщения',
            'recipients': 'Список получателей (клиенты)',
        }

        # Подключаем современный календарь HTML5
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'min': '2026-01-01T00:00',  # Ограничение снизу
                    'max': '2030-12-31T23:59',
                    # Ограничение сверху (не даст раздуть год до 6 символов)
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'min': '2026-01-01T00:00',
                    'max': '2030-12-31T23:59',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'message': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'recipients': forms.SelectMultiple(
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка формата, чтобы календарь считывал существующие даты при редактировании
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']
