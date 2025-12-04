"""
Скрипт для принудительной перезагрузки всех изображений цветов
с правильными Pexels URL
"""

import hashlib
import logging
import os
import re

import django
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower
from flowers.parsers import FlowerParser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def reload_all_images():
    """Принудительно перезагружает все изображения цветов"""
    parser = FlowerParser()
    flowers = Flower.objects.all()

    logger.info(f"Начинаем перезагрузку изображений для {flowers.count()} цветов...")

    updated = 0
    failed = 0

    for flower in flowers:
        try:
            # Получаем URL изображения по названию цветка
            image_url = parser._get_flower_image_url_by_name(flower.name)

            # Если не нашли по русскому названию, пробуем через search_query
            if not image_url:
                # Создаем временный search_query из названия
                search_query = (
                    flower.name.lower()
                    .replace("(", "")
                    .replace(")", "")
                    .replace("шт", "")
                    .strip()
                )
                image_url = parser._get_working_image_url(flower.name, search_query)

            if not image_url:
                logger.warning(
                    f"⚠ Изображение не найдено для '{flower.name}'. Пропускаем."
                )
                failed += 1
                continue

            # Удаляем старое изображение, если оно есть
            if flower.image:
                old_image_path = flower.image.path
                if default_storage.exists(old_image_path):
                    default_storage.delete(old_image_path)
                    logger.info(f"Удалено старое изображение: {old_image_path}")

            # Скачиваем новое изображение
            try:
                response = requests.get(
                    image_url,
                    stream=True,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()

                # Создаем безопасное имя файла
                safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                safe_name = re.sub(r"[-\s]+", "_", safe_name)
                file_extension = image_url.split(".")[-1].split("?")[0]
                if file_extension not in ["jpg", "jpeg", "png", "webp"]:
                    file_extension = "jpg"
                name_hash = hashlib.md5(flower.name.encode()).hexdigest()[:8]
                file_name = f"{safe_name}_{name_hash}.{file_extension}"

                image_content = ContentFile(response.content)
                image_path = default_storage.save(f"flowers/{file_name}", image_content)

                # Обновляем запись цветка
                flower.image = image_path
                flower.image_url = None
                flower.save()

                logger.info(f"✓ Обновлено изображение для '{flower.name}'")
                updated += 1

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"⚠ Не удалось скачать изображение {image_url} "
                    f"для '{flower.name}': {e}"
                )
                failed += 1
            except Exception as e:
                logger.warning(
                    f"⚠ Ошибка при сохранении файла для '{flower.name}': {e}"
                )
                failed += 1

        except Exception as e:
            logger.error(f"Ошибка при обработке цветка '{flower.name}': {e}")
            failed += 1
            continue

    logger.info("=" * 60)
    logger.info("Перезагрузка завершена!")
    logger.info(f"Обновлено: {updated}")
    logger.info(f"Ошибок: {failed}")
    logger.info(f"Всего: {flowers.count()}")


if __name__ == "__main__":
    reload_all_images()
