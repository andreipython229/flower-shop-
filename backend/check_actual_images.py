"""
Проверка реальных изображений в базе данных
"""

import os

import django
import requests
from PIL import Image

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower
from flowers.parsers import FlowerParser


def check_actual_images():
    """Проверяет реальные изображения в базе"""
    parser = FlowerParser()

    # Проверяем конкретные проблемные цветы
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
        "Розовые хризантемы (30 шт)",
        "Желтые хризантемы (30 шт)",
        "Белые хризантемы (30 шт)",
    ]

    print("=" * 80)
    print("ПРОВЕРКА РЕАЛЬНЫХ ИЗОБРАЖЕНИЙ")
    print("=" * 80)

    for flower_name in test_flowers:
        try:
            flower = Flower.objects.get(name=flower_name)

            # Получаем ожидаемый URL
            expected_url = parser._get_flower_image_url_by_name(flower_name)

            print(f"\n{flower_name}:")
            print(f"  Ожидаемый URL: {expected_url}")

            if flower.image:
                # Получаем полный путь к файлу
                image_path = flower.image.path
                print(f"  Файл в БД: {flower.image.name}")
                print(f"  Полный путь: {image_path}")

                # Проверяем, существует ли файл
                if os.path.exists(image_path):
                    file_size = os.path.getsize(image_path)
                    print(f"  Размер файла: {file_size} байт")

                    # Пробуем открыть изображение
                    try:
                        with Image.open(image_path) as img:
                            print(f"  Размер изображения: {img.size}")
                            print(f"  Формат: {img.format}")
                    except Exception as e:
                        print(f"  ⚠ Ошибка при открытии изображения: {e}")
                else:
                    print("  ✗ ФАЙЛ НЕ СУЩЕСТВУЕТ!")
            else:
                print("  ✗ НЕТ ИЗОБРАЖЕНИЯ В БД")

        except Flower.DoesNotExist:
            print(f"\n{flower_name}: ✗ НЕ НАЙДЕН В БД")
        except Exception as e:
            print(f"\n{flower_name}: ✗ ОШИБКА: {e}")

    print("\n" + "=" * 80)
    print("ПРОВЕРКА URL ИЗ PEXELS")
    print("=" * 80)

    # Проверяем несколько URL напрямую
    test_urls = {
        "Красные розы": (
            "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        ),
        "Белые розы": (
            "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        ),
        "Розовые розы": (
            "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        ),
        "Желтые розы": (
            "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        ),
    }

    for name, url in test_urls.items():
        try:
            response = requests.head(
                url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                print(f"✓ {name}: URL работает ({url[:60]}...)")
            else:
                print(f"✗ {name}: URL не работает (статус {response.status_code})")
        except Exception as e:
            print(f"✗ {name}: Ошибка при проверке URL: {e}")


if __name__ == "__main__":
    check_actual_images()
