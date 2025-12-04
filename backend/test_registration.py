#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки регистрации
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

from accounts.serializers import RegisterSerializer

print("=" * 60)
print("ТЕСТИРОВАНИЕ РЕГИСТРАЦИИ")
print("=" * 60)

# Тестовые данные (как на скриншоте)
test_data = {
    "username": "Dima",
    "email": "tunejdec10071994@gmail.com",
    "first_name": "Dima",
    "last_name": "Tumasajn",
    "phone": "+375 25 538 11 51",
    "password": "test123456",  # Замени на реальный пароль
    "password2": "test123456",
}

print("\n📝 Тестовые данные:")
for key, value in test_data.items():
    if "password" in key:
        print(f"  {key}: {'*' * len(str(value))}")
    else:
        print(f"  {key}: {value}")

print("\n🔍 Проверка валидации...")
serializer = RegisterSerializer(data=test_data)

if serializer.is_valid():
    print("✅ Данные валидны!")
    print("\n💾 Попытка создания пользователя...")
    try:
        user = serializer.save()
        print(f"✅ Пользователь создан: {user.username} ({user.email})")
    except Exception as e:
        print(f"❌ Ошибка при создании: {str(e)}")
else:
    print("❌ Ошибки валидации:")
    for field, errors in serializer.errors.items():
        print(f"  {field}: {errors}")

print()
print("=" * 60)
print("\n💡 Требования к паролю:")
print("  - Минимум 8 символов")
print("  - Не должен быть похож на username/email")
print("  - Не должен быть только из цифр")
print("  - Не должен быть в списке популярных паролей")
