"""Поменять местами изображения картинок 104 и 105"""

import logging
import os
import sys
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("ОБМЕН ИЗОБРАЖЕНИЯМИ МЕЖДУ КАРТИНКАМИ 104 И 105")
    logger.info("=" * 80)

    # Находим "Смешанные герберы (15 шт)" - картинка 104
    flower_104 = Flower.objects.filter(
        Q(name__icontains="Смешанные герберы") & Q(name__icontains="15 шт")
    ).first()

    # Находим "Белые герберы (9 шт)" - картинка 105
    flower_105 = Flower.objects.filter(
        Q(name__icontains="Белые герберы") & Q(name__icontains="9 шт")
    ).first()

    if not flower_104:
        logger.error("✗ Цветок 'Смешанные герберы (15 шт)' не найден!")
        sys.exit(1)

    if not flower_105:
        logger.error("✗ Цветок 'Белые герберы (9 шт)' не найден!")
        sys.exit(1)

    logger.info(f"✓ Найден цветок 104: {flower_104.name} (ID: {flower_104.id})")
    logger.info(
        f"  Изображение: {flower_104.image.name if flower_104.image else 'Нет'}"
    )
    logger.info(f"✓ Найден цветок 105: {flower_105.name} (ID: {flower_105.id})")
    logger.info(
        f"  Изображение: {flower_105.image.name if flower_105.image else 'Нет'}"
    )

    if not flower_104.image or not flower_105.image:
        logger.error("✗ У одного из цветков нет изображения!")
        sys.exit(1)

    # Сохраняем пути к изображениям
    image_104_path = (
        flower_104.image.path if os.path.exists(flower_104.image.path) else None
    )
    image_105_path = (
        flower_105.image.path if os.path.exists(flower_105.image.path) else None
    )

    if not image_104_path or not image_105_path:
        logger.error("✗ Не удалось найти файлы изображений!")
        sys.exit(1)

    # Читаем содержимое изображений
    try:
        with open(image_104_path, "rb") as f:
            image_104_content = f.read()

        with open(image_105_path, "rb") as f:
            image_105_content = f.read()

        logger.info("✓ Изображения прочитаны")
        logger.info(f"  Размер изображения 104: {len(image_104_content)} байт")
        logger.info(f"  Размер изображения 105: {len(image_105_content)} байт")
    except Exception as e:
        logger.error(f"✗ Ошибка при чтении изображений: {e}")
        sys.exit(1)

    # Удаляем старые изображения
    try:
        if flower_104.image:
            default_storage.delete(flower_104.image.name)
            logger.info("  🗑️ Старое изображение 104 удалено")

        if flower_105.image:
            default_storage.delete(flower_105.image.name)
            logger.info("  🗑️ Старое изображение 105 удалено")
    except Exception as e:
        logger.warning(f"  ⚠ Не удалось удалить старые изображения: {e}")

    # Сохраняем изображения в обратном порядке
    try:
        import re

        # Картинка 104 получает изображение от картинки 105 (белые герберы)
        safe_name_104 = (
            re.sub(r"[^\w\s-]", "", flower_104.name).strip().replace(" ", "_")
        )
        unique_filename_104 = f"flowers/{safe_name_104}_{int(time.time())}.jpg"
        flower_104.image.save(
            unique_filename_104, ContentFile(image_105_content), save=False
        )
        flower_104.image_url = None
        flower_104.save()
        logger.info(f"  ✅ Изображение 104 сохранено: {flower_104.image.name}")

        # Картинка 105 получает изображение от картинки 104 (смешанные герберы)
        safe_name_105 = (
            re.sub(r"[^\w\s-]", "", flower_105.name).strip().replace(" ", "_")
        )
        unique_filename_105 = f"flowers/{safe_name_105}_{int(time.time())}.jpg"
        flower_105.image.save(
            unique_filename_105, ContentFile(image_104_content), save=False
        )
        flower_105.image_url = None
        flower_105.save()
        logger.info(f"  ✅ Изображение 105 сохранено: {flower_105.image.name}")

        logger.info("=" * 80)
        logger.info(
            "✅ ГОТОВО! Изображения поменяны местами. Обнови страницу в браузере (Ctrl+F5)"
        )
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"✗ Ошибка при сохранении изображений: {e}")
        sys.exit(1)
