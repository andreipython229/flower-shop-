"""
Проверка реального ответа API - что возвращается на фронт
"""

import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.test import RequestFactory

from flowers.models import Flower
from flowers.serializers import FlowerSerializer

# Создаем фейковый request для сериализатора
factory = RequestFactory()
request = factory.get("/api/flowers/")

print("=" * 80)
print("ПРОВЕРКА РЕАЛЬНОГО ОТВЕТА API")
print("=" * 80)

# Проверяем первые 4 проблемных цветка
test_flowers = [
    "Белые розы (35 шт)",
    "Красные розы (35 шт)",
    "Белые фрезии (25 шт)",
    "Желтые альстромерии (25 шт)",
]

for flower_name in test_flowers:
    try:
        flower = Flower.objects.get(name=flower_name)

        # Сериализуем с request для правильного формирования URL
        serializer = FlowerSerializer(flower, context={"request": request})
        data = serializer.data

        print(f"\n{flower_name}:")
        print(f"  ID: {flower.id}")
        print(f"  image (поле в БД): {flower.image.name if flower.image else 'None'}")
        print(f"  image_url (поле в БД): {flower.image_url}")
        print(f"  image_url (из сериализатора): {data.get('image_url')}")
        print(f"  image (из сериализатора): {data.get('image')}")

        # Проверяем файл
        if flower.image:
            import os

            from django.conf import settings

            file_path = os.path.join(settings.MEDIA_ROOT, flower.image.name)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  Файл существует: ✓ ({file_size:,} байт)")
            else:
                print("  Файл НЕ существует: ✗")

    except Flower.DoesNotExist:
        print(f"\n{flower_name}: ✗ Не найден в базе")
    except Exception as e:
        print(f"\n{flower_name}: ✗ Ошибка - {e}")

print("\n" + "=" * 80)
print("ПРОВЕРКА: Что реально приходит на фронт через API")
print("=" * 80)

from rest_framework.test import APIRequestFactory

# Симулируем реальный API запрос
from flowers.views import FlowerViewSet

api_factory = APIRequestFactory()
api_request = api_factory.get("/api/flowers/")
api_request.META["HTTP_HOST"] = "localhost:8000"
api_request.META["SERVER_NAME"] = "localhost"
api_request.META["SERVER_PORT"] = "8000"

viewset = FlowerViewSet()
viewset.request = api_request

# Получаем первые 4 цветка
flowers = Flower.objects.filter(name__in=test_flowers)
serializer = FlowerSerializer(flowers, many=True, context={"request": api_request})

print("\nJSON ответ API для первых 4 цветков:")
print(json.dumps(serializer.data, indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
