"""
Скрипт для ручной загрузки изображений гвоздик
Поддерживает base64 data URI, файлы и URL
"""

import base64
import os

import django
import requests
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def decode_base64_image(data_uri):
    """Декодирует base64 data URI в бинарные данные"""
    try:
        # Формат: data:image/jpeg;base64,/9j/4AAQ...
        header, encoded = data_uri.split(",", 1)
        image_data = base64.b64decode(encoded)
        return image_data
    except Exception as e:
        logger.error(f"Ошибка декодирования base64: {e}")
        return None


def get_image_from_source(source):
    """Получает изображение из разных источников"""
    # Если это base64 data URI
    if source.startswith("data:image"):
        logger.info("  Обнаружен base64 data URI")
        return decode_base64_image(source)

    # Если это URL
    elif source.startswith("http://") or source.startswith("https://"):
        logger.info(f"  Загружаю изображение с URL: {source[:50]}...")
        try:
            response = requests.get(source, timeout=15)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"  Ошибка загрузки: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"  Ошибка при загрузке: {e}")
            return None

    # Если это путь к файлу
    elif os.path.exists(source):
        logger.info(f"  Читаю файл: {source}")
        try:
            with open(source, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"  Ошибка чтения файла: {e}")
            return None

    else:
        logger.error(f"  Неизвестный формат источника: {source[:50]}...")
        return None


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("РУЧНАЯ ЗАГРУЗКА ИЗОБРАЖЕНИЙ ГВОЗДИК")
    logger.info("=" * 80)
    logger.info("Поддерживаемые форматы:")
    logger.info("  1. Base64 data URI (data:image/jpeg;base64,...)")
    logger.info("  2. URL изображения (http://... или https://...)")
    logger.info("  3. Путь к файлу (C:/path/to/image.jpg)")
    logger.info("")

    # Словарь: название букета -> источник изображения
    # ВСТАВЬ СЮДА СВОИ ИЗОБРАЖЕНИЯ!
    # Форматы: base64 data URI, URL или путь к файлу
    images_sources = {
        "Белые гвоздики (25 шт)": "data:image/jpeg;base64,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",  # ВСТАВЬ СЮДА base64 для белых гвоздик (25 шт)
        "Белые гвоздики (15 шт)": "data:image/jpeg;base64,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",  # base64 для белых гвоздик (15 шт)
        "Розовые гвоздики (25 шт)": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAJQApAMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAGAAECBQcEAwj/xAA/EAACAQMCBAQDBgUCAwkAAAABAgMABBEFEgYhMUETIlFhcYGRBxQyQqHBIzOx8PFSYiTR4RUWNENEU2OCov/EABkBAAMBAQEAAAAAAAAAAAAAAAABAgMEBf/EACIRAAMAAgIDAAIDAAAAAAAAAAABAgMREiEUEiMhMUcf/aAAwDAQACEQMRAD8AzunpU9MQqcUhT0ALvT0hT0AKkKVOBQAsU0kaunnGQOdTpnIVC3oKTGi74S1CU295p0Um2dQJo/r5v796M9Ne/laPbKoiA8+6Pnn41ktnevperwaioYmH8Sj8wwcj9a0qx440i4/gWhl8ds+Vozmue0d+HJqODLrV7aG6t2jmGUxzz2rLeJLBLeYLE4YHOF70c3U2pXybIYGRW/M/KqLiHQ0usFbu3Vlbnn1FZ0tM6seTU6ZQ3nDN3bqWjPiKOo6iqOaJ4XKSoUYdQa1W3v4LpQYpFb2zzqOo6Xa6jHtuIwx7N0I+dZ1j+jpx+Qn0zJ6VH2p6dF1p6VKlQBPNPTUqQEx1p6anqhD09KlQA9PSFXfDvCuscRMDp1tiDODcynbGPn3+WaBlKK69O0681OcwafazXMvdYlJ2/E9B9623Qfsu0my2y6rK9/MPyfgiHyHM/M49qN7a3t7OFYbWGKGJRySNNoHypD0ZHov2WancYfVp47ND/5afxJPn2H1NU/2hcJDhq5gFs0ktlcINryEFg4/EpwB7EfOt4LCqbirR4eINFmsJWCO2GikI/A46H9j7E0mVo+Y9U8qhRyJb/l/yqw4CiE3EKsRnZG5FWms/Z9xK2oJFHaxSRMxHjpINiHvu7j6UVcHcCajpA8aeCNpm5MYpdwxzrKv1ZtK/JBYiqI1OB0oH+0m522qRZ6tRxJFcRAq8Mi45HK4H1rKftFvlnvxBHIrhM7ipyM/HvWMy9mt10BUjAYHsKgnKRfc1IKWbc1eaNm5TcQBnlnulHKwki/lipGoQnyAVM1RmRaompE1BjQBE0qbNKgD0p6jTiqESr2tLea7uY7a2ieWaRtqInVjXiOtaf8AZ5YW2mafdp4r3txGGecc45n4VT8TraaTaNdxQ+ZSAq7jgk/wBmiu8mjtrXHnTA5KgrMOOtQLeHa8wFzI2Sc+1NytFLJae9nAOJ5Y5c29xDsPaWMgj6UU2d/e3NgHPJdWjQSKSBbOCxx15Z5dR1FZU2KN+EbARaTdXT4y6Id2P9RP7Csqxyjqx+VkdI6ry4uWdvu+lb3/8AcuW3/p0/SvSK3muNMmGpW8dsysD4sS4Ur3AHr8KJ7/XLS2jit7OxN3dlFLAeVVOOYJxVTq73N2los5XJfzIgwq/371lwR3VmaW2cHBGgW82pJNegOw8yQnmF9M13cVOLfXZgULZRdoA7Yri09r/Sb0TLbSMgOMhSdw+VS4p1mzutlzIxt51TY8cgwSOxH60muU6+mXPVb+HRwpLh7lnP+n5nnXLxVxJBATbW8sb3Bk5qG/D8aCLjiC8KGG0drePdnchw7fE/tVOXYybySWJySTzJraI0jz8t8qbRdyytLI0kjFnYkkmvM1FW3KreozTE1ZmI1A0iajmgBGlUaegD2pjSpUxD04pUqAHom+ztQeKI8jP8CQ/oKVKhAaPq0sjWkx3kBIywA5DNY3rE0k1zO0rFmI6mlSpsSKeJQ88St0Z1B+BNaHCog4a14xeXw5kRMflAU4A5+ppUqzv2jTH+wuD7+5vNPLXMniOkhTcVGWAAxk9+tWd/Ky3Vuo6ZP9KVKj4zqxPa7LGfyWu8cysYOD06Vj+sX09/qEs9wQW3lQAOSgZwBSpUo9med9HA3QUwpUq1ZzFjbE+AnwqZpqVSBE0xNKlQMalSpUAf/2Q==",  # base64 для розовых гвоздик (25 шт)
        "Розовые гвоздики (15 шт)": None,  # Вставь сюда base64, URL или путь к файлу
    }

    # Если пользователь передал base64 для белых гвоздик (25 шт)
    # Пример использования:
    # images_sources['Белые гвоздики (25 шт)'] = 'data:image/jpeg;base64,/9j/4AAQ...'

    updated = 0
    skipped = 0

    for flower_name, image_source in images_sources.items():
        if image_source is None:
            logger.warning(f"  ⚠ Пропущено: {flower_name} (нет источника изображения)")
            skipped += 1
            continue

        logger.info("-" * 80)
        logger.info(f"Обрабатываем: {flower_name}")

        # Ищем букет в базе
        flowers = Flower.objects.filter(name=flower_name, in_stock=True)

        if not flowers.exists():
            logger.warning(f"  ⚠ Не найдено: {flower_name}")
            skipped += 1
            continue

        flower = flowers.first()
        logger.info(f"  Найден: ID {flower.id}")

        # Получаем изображение
        image_data = get_image_from_source(image_source)

        if not image_data:
            logger.warning("  ⚠ Не удалось получить изображение")
            skipped += 1
            continue

        try:
            # Генерируем имя файла
            import time

            timestamp = int(time.time())
            safe_name = (
                flower_name.replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
                .replace('"', "")
                .replace("/", "_")
            )
            filename = f"flowers/{safe_name}_{timestamp}.jpg"

            # Удаляем старое изображение
            if flower.image:
                try:
                    old_path = flower.image.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                        logger.info("  ✓ Старое изображение удалено")
                except Exception as e:
                    logger.warning(f"  ⚠ Не удалось удалить старое изображение: {e}")

            # Сохраняем новое изображение
            flower.image.save(filename, ContentFile(image_data), save=True)
            logger.info(f"  ✅ Изображение сохранено: {filename}")
            updated += 1

        except Exception as e:
            logger.error(f"  ✗ Ошибка при сохранении: {e}")
            skipped += 1

        logger.info("")

    logger.info("=" * 80)
    logger.info(f"Завершено! Обновлено: {updated}, Пропущено: {skipped}")
    logger.info("=" * 80)
    logger.info("")
    logger.info("ИНСТРУКЦИЯ:")
    logger.info("1. Открой файл upload_carnations_manual.py")
    logger.info("2. В словаре images_sources вставь свои изображения:")
    logger.info("   - Base64: 'data:image/jpeg;base64,/9j/4AAQ...'")
    logger.info("   - URL: 'https://example.com/image.jpg'")
    logger.info("   - Файл: 'C:/path/to/image.jpg'")
    logger.info("3. Запусти: python upload_carnations_manual.py")
    logger.info("=" * 80)
