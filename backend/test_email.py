#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки отправки email
"""
import os
import sys
from pathlib import Path

import django

# Настройка Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("ТЕСТИРОВАНИЕ ОТПРАВКИ EMAIL")
print("=" * 60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    print("ℹ️  Используется консольный режим - письма НЕ отправляются реально")
    print("   Они будут видны в консоли Django сервера")
    print()
    print("📧 Тестовое письмо будет показано ниже:")
    print("-" * 60)

    send_mail(
        subject="Тестовое письмо от Flower Shop",
        message="Это тестовое письмо. Если ты видишь это в консоли - всё работает!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["grant10071994@gmail.com"],
        fail_silently=False,
    )

    print("-" * 60)
    print("✅ Письмо выведено в консоль выше")

else:
    print("📤 Попытка отправить реальное письмо через SMTP...")
    print()

    try:
        send_mail(
            subject="Тестовое письмо от Flower Shop",
            message=(
                "Это тестовое письмо. "
                "Если ты получил его - email настроен правильно!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["grant10071994@gmail.com"],
            fail_silently=False,
        )

        print("✅ Письмо отправлено!")
        print("📧 Проверь почту grant10071994@gmail.com (включая папку 'Спам')")

    except Exception as e:
        print(f"❌ ОШИБКА при отправке: {str(e)}")
        print()
        print("💡 Возможные причины:")
        print("   1. Неверный пароль приложения")
        print("   2. Двухэтапная аутентификация не включена")
        print("   3. Проблемы с интернет-соединением")
        print("   4. Gmail блокирует отправку")

print()
print("=" * 60)
