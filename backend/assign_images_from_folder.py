"""
Скрипт для привязки изображений из папки media/flowers к цветам по ключевым словам
"""

import logging
import os
import re
from pathlib import Path

import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def normalize_name(name):
    """Нормализует название для поиска"""
    return re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()


def find_best_match(flower_name, image_files):
    """Находит лучшее совпадение изображения для цветка"""
    normalized = normalize_name(flower_name)

    # Маппинг ключевых слов
    keywords = {
        "красные": ["red", "красн"],
        "белые": ["white", "бел"],
        "розовые": ["pink", "розов"],
        "желтые": ["yellow", "желт"],
        "синие": ["blue", "син"],
        "оранжевые": ["orange", "оранж"],
        "фиолетовые": ["purple", "фиолет"],
        "розы": ["rose", "roses", "роз"],
        "гвоздики": ["carnation", "carnations", "гвоздик"],
        "герберы": ["gerbera", "gerberas", "гербер"],
        "ромашки": ["daisy", "daisies", "ромашк"],
        "тюльпаны": ["tulip", "tulips", "тюльпан"],
        "хризантемы": ["chrysanthemum", "chrysanthemums", "хризантем"],
        "пионы": ["peony", "peonies", "пион"],
        "лилии": ["lily", "lilies", "лили"],
        "ирисы": ["iris", "irises", "ирис"],
        "орхидеи": ["orchid", "orchids", "орхиде"],
        "альстромерии": ["alstroemeria", "альстром"],
        "фрезии": ["freesia", "фрези"],
        "астры": ["aster", "asters", "астр"],
        "гладиолусы": ["gladiolus", "гладиолус"],
        "эустомы": ["eustoma", "эустом"],
    }

    # Извлекаем ключевые слова из названия цветка
    flower_keywords = []
    for key, values in keywords.items():
        if key in normalized:
            flower_keywords.extend(values)

    if not flower_keywords:
        return None

    # Ищем файл с максимальным совпадением
    best_match = None
    best_score = 0

    for img_file in image_files:
        img_name_lower = img_file.stem.lower()
        score = 0

        for keyword in flower_keywords:
            if keyword in img_name_lower:
                score += 1

        if score > best_score:
            best_match = img_file
            best_score = score

    return best_match if best_score > 0 else None


def assign_images():
    """Привязывает изображения из папки к цветам"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"Папка {media_path} не существует!")
        return

    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info(f"Найдено {len(image_files)} изображений в папке")

    if len(image_files) == 0:
        logger.error("Нет изображений в папке!")
        return

    logger.info(f"Начинаем привязку изображений для {flowers.count()} цветов...")

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            # ПРИНУДИТЕЛЬНО перепривязываем все изображения
            # (убрали проверку, чтобы исправить неправильные изображения)

            # Ищем подходящее изображение
            matching_image = find_best_match(flower.name, image_files)

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
                    file_name = f"{safe_name}{matching_image.suffix}"

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

    logger.info("\n" + "=" * 60)
    logger.info(
        f"Завершено! Обновлено: {updated}, Пропущено: {skipped}, Ошибок: {failed}"
    )


if __name__ == "__main__":
    assign_images()
