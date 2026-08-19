from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    is_verified = models.BooleanField(default=False,
                                      verbose_name='Верифицирован')
    verification_token = models.CharField(max_length=100, blank=True,
                                          null=True)

    # Роль менеджера определяем
    # Булево для проверки в шаблонах и view.
    is_manager = models.BooleanField(default=False, verbose_name='Менеджер')
    is_blocked = models.BooleanField(default=False,
                                     verbose_name='Заблокирован')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
