from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомного пользователя без username (вход по email)."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    # Убираем стандартный username, делаем email главным логином
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    # Поля по требованиям ТЗ
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=150, blank=True, null=True, verbose_name="Отчество")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")
    phone_number = models.CharField(max_length=35, blank=True, null=True, verbose_name="Номер телефона")

    # Подключаем наш менеджер
    objects = CustomUserManager()

    # Указываем вход по email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
