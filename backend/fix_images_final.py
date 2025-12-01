"""
ФИНАЛЬНОЕ РЕШЕНИЕ: Используем только файлы, которые точно соответствуют названию
Исключаем файлы, которые уже использовались для других цветов
"""

import hashlib
import os
import re
import time
from pathlib import Path

import django
from django.conf import settings
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def normalize_flower_name(name):
    """Нормализует название цветка для точного сравнения"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", "_", clean)  # Заменяем пробелы на подчеркивания
    return clean


def get_file_hash(file_path):
    """Вычисляет MD5 хеш файла"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None


def find_exact_match(flower_name, image_files, used_hashes):
    """
    Находит ТОЧНОЕ совпадение по названию
    Приоритет: точное совпадение > частичное совпадение
    """
    normalized = normalize_flower_name(flower_name)

    # Ищем файлы с точным совпадением
    exact_matches = []
    partial_matches = []

    for img_file in image_files:
        img_name_lower = img_file.stem.lower()
        # Убираем timestamp и хеши
        clean_img_name = re.sub(r"_\d+$", "", img_name_lower)
        clean_img_name = re.sub(r"_[a-zA-Z0-9]{8,}$", "", clean_img_name)

        # Вычисляем хеш
        file_hash = get_file_hash(img_file)
        if not file_hash or file_hash in used_hashes:
            continue

        # Проверяем точное совпадение
        if normalized == clean_img_name:
            exact_matches.append((img_file, file_hash, 100))
        # Проверяем частичное совпадение (все слова из названия есть в имени файла)
        elif all(
            word in clean_img_name for word in normalized.split("_") if len(word) > 2
        ):
            # Считаем процент совпадения
            flower_words = set(normalized.split("_"))
            file_words = set(clean_img_name.split("_"))
            match_percent = len(flower_words & file_words) / len(flower_words) * 100
            if match_percent >= 80:  # Минимум 80% совпадения
                partial_matches.append((img_file, file_hash, match_percent))

    # Возвращаем лучшее точное совпадение
    if exact_matches:
        return exact_matches[0][0], exact_matches[0][1]

    # Если нет точного, возвращаем лучшее частичное
    if partial_matches:
        partial_matches.sort(key=lambda x: x[2], reverse=True)
        return partial_matches[0][0], partial_matches[0][1]

    return None, None


def fix_images_final():
    """Финальное исправление изображений с точным совпадением"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"❌ Папка {media_path} не существует!")
        return

    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info("=" * 80)
    logger.info("ФИНАЛЬНОЕ РЕШЕНИЕ: Точное совпадение по названию")
    logger.info(f"Найдено {len(image_files)} файлов в папке")
    logger.info("=" * 80)
    logger.info(f"\nОбработка {flowers.count()} цветов...\n")

    updated = 0
    skipped = 0
    failed = 0
    used_hashes = set()

    for flower in flowers:
        try:
            matching_image, file_hash = find_exact_match(
                flower.name, image_files, used_hashes
            )

            if not matching_image:
                logger.warning(f"⚠ Не найдено точное совпадение для '{flower.name}'")
                skipped += 1
                continue

            used_hashes.add(file_hash)

            # Удаляем старое
            if flower.image:
                try:
                    old_path = flower.image.path
                    if os.path.exists(old_path) and old_path != str(matching_image):
                        os.remove(old_path)
                except Exception:
                    pass

            # Сохраняем новое
            try:
                with open(matching_image, "rb") as f:
                    safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                    safe_name = re.sub(r"[-\s]+", "_", safe_name)
                    timestamp = int(time.time())
                    file_name = f"{safe_name}_{timestamp}{matching_image.suffix}"

                    flower.image.save(file_name, File(f), save=True)
                    flower.image_url = None
                    flower.save()

                    logger.info(f"✓ '{flower.name}' -> {matching_image.name}")
                    updated += 1

            except Exception as e:
                logger.warning(f"⚠ Ошибка для '{flower.name}': {e}")
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка для '{flower.name}': {e}")
            failed += 1

    logger.info("\n" + "=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )
    logger.info(f"Использовано уникальных файлов: {len(used_hashes)}")
    logger.info("=" * 80)
    logger.info("\n⚠ ВАЖНО: Если изображения все еще неправильные,")
    logger.info("значит файлы в папке содержат неправильные изображения.")
    logger.info(
        "Нужно найти правильные файлы вручную или использовать другой источник."
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    fix_images_final()
