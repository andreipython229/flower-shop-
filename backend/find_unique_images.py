"""
Поиск уникальных изображений для каждого цветка
Исключает файлы с одинаковым содержимым
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
    """Нормализует название цветка"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", " ", clean)
    return clean


def get_file_hash(file_path):
    """Вычисляет MD5 хеш файла"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None


def find_unique_image(flower_name, image_files, used_hashes):
    """
    Находит уникальное изображение для цветка
    Исключает файлы, которые уже используются другими цветами
    """
    normalized = normalize_flower_name(flower_name)

    # Извлекаем цвет и тип
    colors = [
        "красные",
        "белые",
        "розовые",
        "желтые",
        "синие",
        "оранжевые",
        "фиолетовые",
        "бордовые",
        "персиковые",
        "двухцветные",
    ]
    flower_types = [
        "розы",
        "гвоздики",
        "герберы",
        "ромашки",
        "васильки",
        "тюльпаны",
        "хризантемы",
        "пионы",
        "лилии",
        "ирисы",
        "орхидеи",
        "альстромерии",
        "фрезии",
        "астры",
        "гладиолусы",
        "эустомы",
    ]

    found_color = None
    found_flower = None

    for color in colors:
        if color in normalized:
            found_color = color
            break

    for flower in flower_types:
        if flower in normalized:
            found_flower = flower
            break

    # Ищем файлы с максимальным совпадением
    candidates = []

    for img_file in image_files:
        img_name_lower = img_file.stem.lower()
        clean_img_name = re.sub(r"_\d+$", "", img_name_lower)
        clean_img_name = re.sub(r"_[a-zA-Z0-9]{8,}$", "", clean_img_name)

        # Вычисляем хеш файла
        file_hash = get_file_hash(img_file)
        if not file_hash:
            continue

        # Пропускаем файлы, которые уже используются
        if file_hash in used_hashes:
            continue

        score = 0
        has_color = False
        has_flower = False

        # Проверяем цвет
        if found_color:
            color_variants = {
                "красные": ["красн", "red"],
                "белые": ["бел", "white"],
                "розовые": ["розов", "pink"],
                "желтые": ["желт", "yellow"],
                "синие": ["син", "blue"],
                "оранжевые": ["оранж", "orange"],
                "фиолетовые": ["фиолет", "purple"],
                "бордовые": ["бордов", "burgundy"],
                "персиковые": ["персиков", "peach"],
            }
            for variant in color_variants.get(found_color, []):
                if variant in clean_img_name:
                    score += 10
                    has_color = True
                    break

        # Проверяем тип цветка
        if found_flower:
            flower_variants = {
                "розы": ["роз", "rose"],
                "гвоздики": ["гвоздик", "carnation"],
                "герберы": ["гербер", "gerbera"],
                "ромашки": ["ромашк", "daisy"],
                "васильки": ["василек", "васильк", "cornflower"],
                "тюльпаны": ["тюльпан", "tulip"],
                "хризантемы": ["хризантем", "chrysanthemum"],
                "пионы": ["пион", "peony"],
                "лилии": ["лили", "lily"],
                "ирисы": ["ирис", "iris"],
                "орхидеи": ["орхиде", "orchid"],
                "альстромерии": ["альстром", "alstroemeria"],
                "фрезии": ["фрези", "freesia"],
                "астры": ["астр", "aster"],
                "гладиолусы": ["гладиолус", "gladiolus"],
                "эустомы": ["эустом", "eustoma"],
            }
            for variant in flower_variants.get(found_flower, []):
                if variant in clean_img_name:
                    score += 15
                    has_flower = True
                    break

        if has_color and has_flower:
            score += 20

        flower_name_clean = normalized.replace(" ", "_")
        if flower_name_clean in clean_img_name:
            score += 30

        if score > 0:
            candidates.append((img_file, score, has_color, has_flower, file_hash))

    if not candidates:
        return None, None

    # Сортируем по score
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Возвращаем лучшее совпадение с цветом и типом
    for candidate in candidates:
        if candidate[2] and candidate[3]:  # Есть и цвет, и тип
            return candidate[0], candidate[4]  # Возвращаем файл и хеш

    # Если нет полного совпадения, возвращаем лучшее
    return candidates[0][0], candidates[0][4]


def assign_unique_images():
    """Привязывает уникальные изображения к цветам"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"❌ Папка {media_path} не существует!")
        return

    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info("=" * 80)
    logger.info(f"Найдено {len(image_files)} локальных изображений")
    logger.info("Используем УНИКАЛЬНЫЕ файлы (исключаем дубликаты по содержимому)")
    logger.info("=" * 80)
    logger.info(f"\nОбработка {flowers.count()} цветов...\n")

    if len(image_files) == 0:
        logger.error("❌ Нет изображений в папке!")
        return

    updated = 0
    skipped = 0
    failed = 0
    used_hashes = set()  # Храним хеши уже использованных файлов

    for flower in flowers:
        try:
            matching_image, file_hash = find_unique_image(
                flower.name, image_files, used_hashes
            )

            if not matching_image:
                logger.warning(
                    f"⚠ Не найдено уникальное изображение для '{flower.name}'"
                )
                skipped += 1
                continue

            # Помечаем хеш как использованный
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

                    hash_short = file_hash[:8]
                    logger.info(
                        f"✓ '{flower.name}' -> {matching_image.name} "
                        f"(hash: {hash_short})"
                    )
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


if __name__ == "__main__":
    assign_unique_images()
