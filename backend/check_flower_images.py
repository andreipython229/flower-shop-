"""
Скрипт для проверки изображений цветов в базе данных
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower


def check_flower_images():
    """Проверяет изображения для цветов"""
    flowers = Flower.objects.all()[:10]  # Первые 10 для проверки

    print("=" * 80)
    print("ПРОВЕРКА ИЗОБРАЖЕНИЙ В БАЗЕ ДАННЫХ")
    print("=" * 80)

    for flower in flowers:
        print(f"\n{flower.name}:")
        if flower.image:
            print(f"  ✓ Есть локальный файл: {flower.image.name}")
            print(
                f"  Путь: {
        flower.image.path if hasattr(
            flower.image,
             'path') else 'N/A'}"
            )
        else:
            print("  ✗ Нет локального файла")

        if flower.image_url:
            print(f"  ✓ Есть URL: {flower.image_url}")
        else:
            print("  ✗ Нет URL")

    print("\n" + "=" * 80)
    print(f"Всего цветов в базе: {Flower.objects.count()}")


if __name__ == "__main__":
    check_flower_images()
