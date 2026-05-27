import re
import logging
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

logger = logging.getLogger('users')


def validate_phone(value):
    pattern = r'^\+375 \((29|33|44|25)\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Номер телефона должен быть в формате +375 (29) XXX-XX-XX'
        )


def validate_age_18(value):
    today = timezone.now().date()
    age = (today - value).days // 365
    if age < 18:
        raise ValidationError('Возраст должен быть не менее 18 лет.')


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_EMPLOYEE = 'employee'
    ROLE_CLIENT = 'client'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Администратор'),
        (ROLE_EMPLOYEE, 'Сотрудник'),
        (ROLE_CLIENT, 'Клиент'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CLIENT, verbose_name='Роль')
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone], verbose_name='Телефон')
    birth_date = models.DateField(blank=True, null=True, validators=[validate_age_18], verbose_name='Дата рождения')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    def is_employee(self):
        return self.role == self.ROLE_EMPLOYEE

    def is_client(self):
        return self.role == self.ROLE_CLIENT
