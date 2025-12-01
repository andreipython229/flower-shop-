"""
Проверка того, что возвращает API для фронтенда
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.test import RequestFactory

from flowers.models import Flower
from flowers.serializers import FlowerSerializer


def test_api_response():
    """Проверяет, что возвращает API"""
    factory = RequestFactory()
    request = factory.get("/api/flowers/")

    # Получаем проблемные цветы
    test_flowers = [
        "Белые розы (35 шт)",
        "Красные розы (35 шт)",
        "Белые фрезии (25 шт)",
        "Желтые альстромерии (25 шт)",
        "Розовые альстромерии (25 шт)",
        "Розовые орхидеи (5 шт)",
        "Белые орхидеи (5 шт)",
        "Фиолетовые ирисы (20 шт)",
        "Синие ирисы (20 шт)",
        "Розовые лилии (9 шт)",
        "Белые лилии (9 шт)",
        "Белые пионы (7 шт)",
        "Розовые пионы (7 шт)",
    ]

    print("=" * 80)
    print("ПРОВЕРКА ОТВЕТА API")
    print("=" * 80)

    for flower_name in test_flowers:
        try:
            flower = Flower.objects.get(name=flower_name)
            serializer = FlowerSerializer(flower, context={"request": request})
            data = serializer.data

            print(f"\n{flower_name}:")
            print(f"  image_url (API): {data.get('image_url', 'НЕТ')}")
            print(f"  image (API): {data.get('image', 'НЕТ')}")

            if flower.image:
                # Проверяем, что файл существует
                if os.path.exists(flower.image.path):
                    print(f"  ✓ Файл существует: {flower.image.path}")
                else:
                    print(f"  ✗ Файл НЕ существует: {flower.image.path}")
        except Flower.DoesNotExist:
            print(f"\n{flower_name}: ✗ НЕ НАЙДЕН В БД")
        except Exception as e:
            print(f"\n{flower_name}: ✗ ОШИБКА: {e}")

    print("\n" + "=" * 80)
    print("ПРОВЕРКА БАЗОВОГО URL")
    print("=" * 80)

    # Проверяем базовый URL для медиа файлов
    from django.conf import settings

    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"DEBUG: {settings.DEBUG}")


if __name__ == "__main__":
    test_api_response()
