"""
Поиск правильных изображений из локальной папки
Используем более умный алгоритм поиска
"""

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


def find_best_image(flower_name, image_files):
    """
    Умный поиск изображения с приоритетом:
    1. Точное совпадение названия (без количества)
    2. Совпадение по цвету + типу цветка
    3. Совпадение только по типу цветка
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
        # Убираем timestamp и хеши
        clean_img_name = re.sub(r"_\d+$", "", img_name_lower)
        clean_img_name = re.sub(r"_[a-zA-Z0-9]{8,}$", "", clean_img_name)

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

        # Бонус за полное совпадение
        if has_color and has_flower:
            score += 20

        # Бонус за точное совпадение нормализованного названия
        flower_name_clean = normalized.replace(" ", "_")
        if flower_name_clean in clean_img_name:
            score += 30

        if score > 0:
            candidates.append((img_file, score, has_color, has_flower))

    if not candidates:
        return None

    # Сортируем по score
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Возвращаем лучшее совпадение, которое имеет и цвет, и тип
    for candidate in candidates:
        if candidate[2] and candidate[3]:  # Есть и цвет, и тип
            return candidate[0]

    # Если нет полного совпадения, возвращаем лучшее
    return candidates[0][0]


def fix_images_from_local():
    """Исправляет изображения используя локальные файлы"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"❌ Папка {media_path} не существует!")
        return

    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info("=" * 80)
    logger.info(f"Найдено {len(image_files)} локальных изображений")
    logger.info("Используем УМНЫЙ поиск с приоритетом точных совпадений")
    logger.info("=" * 80)
    logger.info(f"\nОбработка {flowers.count()} цветов...\n")

    if len(image_files) == 0:
        logger.error("❌ Нет изображений в папке!")
        return

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            matching_image = find_best_image(flower.name, image_files)

            if not matching_image:
                logger.warning(f"⚠ Не найдено изображение для '{flower.name}'")
                skipped += 1
                continue

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
    logger.info("=" * 80)


if __name__ == "__main__":
    fix_images_from_local()
