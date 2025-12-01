"""
Скрипт для исправления изображений цветов из существующих файлов в папке media/flowers
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


def normalize_flower_name(name):
    """Нормализует название цветка для поиска"""
    # Убираем количество в скобках
    clean_name = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    # Убираем кавычки и лишние пробелы
    clean_name = clean_name.replace('"', "").replace("«", "").replace("»", "")
    clean_name = re.sub(r"\s+", " ", clean_name)
    return clean_name


def find_matching_image(flower_name, image_files):
    """Находит подходящее изображение для цветка"""
    normalized = normalize_flower_name(flower_name)

    # Извлекаем ключевые слова из названия
    keywords = []

    # Цвета
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
    ]
    for color in colors:
        if color in normalized:
            keywords.append(color)
            break

    # Типы цветов
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
    for ftype in flower_types:
        if ftype in normalized:
            keywords.append(ftype)
            break

    # Ищем файл, который содержит ключевые слова
    best_match = None
    best_score = 0

    for img_file in image_files:
        img_name_lower = img_file.stem.lower()
        score = 0

        # Подсчитываем совпадения ключевых слов
        for keyword in keywords:
            if keyword in img_name_lower:
                score += 1

        # Если все ключевые слова совпали - это идеальный вариант
        if score == len(keywords) and len(keywords) > 0:
            best_match = img_file
            best_score = score
            break
        elif score > best_score:
            best_match = img_file
            best_score = score

    return best_match


def fix_flower_images():
    """Исправляет изображения для всех цветов из существующих файлов"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"Папка {media_path} не существует!")
        return

    # Получаем список всех изображений
    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info(f"Найдено {len(image_files)} изображений в папке media/flowers")

    if len(image_files) == 0:
        logger.error("Нет изображений в папке media/flowers!")
        return

    logger.info(f"Начинаем исправление изображений для {flowers.count()} цветов...")

    updated = 0
    failed = 0
    skipped = 0

    for flower in flowers:
        try:
            # Если уже есть правильное изображение, пропускаем
            if flower.image:
                current_name = Path(flower.image.name).stem.lower()
                flower_name_normalized = normalize_flower_name(flower.name)

                # Проверяем, соответствует ли текущее изображение названию
                keywords_match = True
                if "розы" in flower_name_normalized and "роз" not in current_name:
                    keywords_match = False
                elif "фрезии" in flower_name_normalized and "фрези" not in current_name:
                    keywords_match = False
                elif (
                    "альстромерии" in flower_name_normalized
                    and "альстром" not in current_name
                ):
                    keywords_match = False

                if keywords_match:
                    logger.info(f"✓ '{flower.name}' уже имеет подходящее изображение")
                    skipped += 1
                    continue

            # Ищем подходящее изображение
            matching_image = find_matching_image(flower.name, image_files)

            if not matching_image:
                logger.warning(
                    f"⚠ Не найдено подходящее изображение для '{flower.name}'"
                )
                skipped += 1
                continue

            # Удаляем старое изображение, если оно есть
            if flower.image:
                try:
                    old_image_path = flower.image.path
                    if os.path.exists(old_image_path) and old_image_path != str(
                        matching_image
                    ):
                        os.remove(old_image_path)
                except Exception as e:
                    logger.warning(f"  Не удалось удалить старое изображение: {e}")

            # Сохраняем новое изображение
            try:
                with open(matching_image, "rb") as f:
                    # Создаем имя файла на основе названия цветка
                    safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                    safe_name = re.sub(r"[-\s]+", "_", safe_name)
                    file_extension = matching_image.suffix
                    file_name = f"{safe_name}{file_extension}"

                    # Сохраняем файл
                    flower.image.save(file_name, File(f), save=True)
                    flower.image_url = None
                    flower.save()

                    logger.info(
                        f"✓ Обновлено изображение для '{flower.name}' -> {matching_image.name}"
                    )
                    updated += 1

            except Exception as e:
                logger.warning(
                    f"⚠ Ошибка при сохранении файла для '{flower.name}': {e}"
                )
                failed += 1

        except Exception as e:
            logger.error(f"✗ Ошибка при обработке цветка '{flower.name}': {e}")
            failed += 1
            continue

    logger.info("\n" + "=" * 60)
    logger.info("Исправление завершено!")
    logger.info(f"Обновлено: {updated}")
    logger.info(f"Пропущено: {skipped}")
    logger.info(f"Ошибок: {failed}")
    logger.info(f"Всего: {flowers.count()}")


if __name__ == "__main__":
    fix_flower_images()
