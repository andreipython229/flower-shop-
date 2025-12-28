#!/usr/bin/env python
"""Скрипт для создания суперпользователя на продакшн"""
import os
import django

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


def create_superuser():
    """Создаёт суперпользователя, если его ещё нет"""
    username = os.environ.get("SUPERUSER_USERNAME", "andrei2")
    email = os.environ.get("SUPERUSER_EMAIL", "admin@flowershop.com")
    password = os.environ.get("SUPERUSER_PASSWORD")

    if not password:
        print("⚠️  SUPERUSER_PASSWORD не установлен в переменных окружения")
        print("   Суперпользователь не будет создан автоматически")
        return

    # Проверяем, существует ли уже пользователь
    if User.objects.filter(username=username).exists():
        print(f"✓ Пользователь '{username}' уже существует")
        # Обновляем его до суперпользователя, если нужно
        user = User.objects.get(username=username)
        if not user.is_superuser:
            user.is_superuser = True
            user.is_staff = True
            user.set_password(password)
            user.save()
            print(f"✓ Пользователь '{username}' теперь суперпользователь")
        else:
            print(f"✓ Пользователь '{username}' уже является суперпользователем")
        return

    # Создаём нового суперпользователя
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        print(f"✓ Суперпользователь '{username}' успешно создан!")
    except Exception as e:
        print(f"✗ Ошибка при создании суперпользователя: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Создание суперпользователя...")
    print("=" * 60)
    create_superuser()
    print("=" * 60)
