"""
Скрипт с ТОЧНЫМ маппингом названий цветов на правильные файлы изображений
Использует строгое соответствие: название цветка -> конкретный файл
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


def normalize_name(name):
    """Нормализует название для поиска"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", "_", clean)
    return clean


def build_exact_mapping(image_files):
    """
    Строит точный маппинг: нормализованное название -> файл
    """
    mapping = {}

    # Сначала создаем маппинг по именам файлов
    for img_file in image_files:
        # Нормализуем имя файла
        file_stem = img_file.stem.lower()
        # Убираем timestamp и хеши
        clean_name = re.sub(r"_\d+$", "", file_stem)
        clean_name = re.sub(r"_[a-zA-Z0-9]{8,}$", "", clean_name)

        # Добавляем в маппинг
        if clean_name not in mapping:
            mapping[clean_name] = []
        mapping[clean_name].append(img_file)

    return mapping


def find_exact_image(flower_name, image_files, mapping):
    """
    Находит точное изображение для цветка
    Приоритет:
    1. Точное совпадение нормализованного названия
    2. Совпадение по ключевым словам (цвет + тип цветка)
    """
    normalized = normalize_name(flower_name)

    # ПРИОРИТЕТ 1: Точное совпадение
    if normalized in mapping:
        files = mapping[normalized]
        if files:
            logger.info(f"  ✓ Точное совпадение: {files[0].name}")
            return files[0]

    # ПРИОРИТЕТ 2: Поиск по ключевым словам
    # Извлекаем цвет и тип цветка
    color_keywords = {
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

    flower_keywords = {
        "розы": ["роз", "rose", "roses"],
        "гвоздики": ["гвоздик", "carnation"],
        "герберы": ["гербер", "gerbera"],
        "ромашки": ["ромашк", "daisy"],
        "васильки": ["васильк", "cornflower"],
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

    found_color = None
    found_flower = None

    for ru_color, keywords in color_keywords.items():
        if ru_color in normalized:
            found_color = keywords
            break

    for ru_flower, keywords in flower_keywords.items():
        if ru_flower in normalized:
            found_flower = keywords
            break

    # Ищем файлы, которые содержат и цвет, и тип цветка
    best_matches = []

    for img_file in image_files:
        file_stem = img_file.stem.lower()
        clean_name = re.sub(r"_\d+$", "", file_stem)
        clean_name = re.sub(r"_[a-zA-Z0-9]{8,}$", "", clean_name)

        score = 0
        has_color = False
        has_flower = False

        if found_color:
            for kw in found_color:
                if kw in clean_name:
                    score += 5
                    has_color = True
                    break

        if found_flower:
            for kw in found_flower:
                if kw in clean_name:
                    score += 10
                    has_flower = True
                    break

        # Бонус за оба совпадения
        if has_color and has_flower:
            score += 20

        if score > 0:
            best_matches.append((img_file, score, clean_name))

    if best_matches:
        # Сортируем по score
        best_matches.sort(key=lambda x: x[1], reverse=True)
        best_file, best_score, matched_name = best_matches[0]
        logger.info(
            f"  ✓ Найдено по ключевым словам: {best_file.name} (score: {best_score})"
        )
        return best_file

    return None


def load_images():
    """Загружает изображения с точным маппингом"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"❌ Папка {media_path} не существует!")
        return

    # Загружаем все изображения
    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info("=" * 80)
    logger.info(f"Найдено {len(image_files)} локальных изображений")
    logger.info("=" * 80)

    if len(image_files) == 0:
        logger.error("❌ Нет изображений в папке!")
        return

    # Строим маппинг
    logger.info("Строим точный маппинг названий...")
    mapping = build_exact_mapping(image_files)
    logger.info(f"Создано {len(mapping)} записей в маппинге")
    logger.info(f"\nНачинаем обработку {flowers.count()} цветов...\n")

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            # Ищем точное изображение
            matching_image = find_exact_image(flower.name, image_files, mapping)

            if not matching_image:
                logger.warning(f"⚠ Не найдено изображение для '{flower.name}'")
                skipped += 1
                continue

            # Удаляем старое изображение
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
                logger.warning(f"⚠ Ошибка при сохранении для '{flower.name}': {e}")
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка для '{flower.name}': {e}")
            failed += 1

    logger.info("\n" + "=" * 80)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )
    logger.info("=" * 80)
    logger.info("\nВАЖНО: Проверь несколько изображений в браузере!")
    logger.info(
        "Если они правильные - отлично! Если нет - нужно улучшить логику поиска."
    )
    logger.info("=" * 80)


if __name__ == "__main__":
    load_images()
