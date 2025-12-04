"""
Загрузка изображений из локальной папки media/flowers/
С улучшенной логикой поиска правильных изображений
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
    """Нормализует название цветка для поиска"""
    # Убираем количество в скобках
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    # Убираем кавычки
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    # Убираем лишние пробелы
    clean = re.sub(r"\s+", " ", clean)
    return clean


def find_best_local_image(flower_name, image_files):
    """
    Находит лучшее локальное изображение для цветка
    Использует умный поиск по ключевым словам
    """
    normalized = normalize_flower_name(flower_name)

    # Маппинг цветов (русский -> английский и варианты)
    color_keywords = {
        "красные": ["red", "красн", "красная", "красный"],
        "белые": ["white", "бел", "белая", "белый"],
        "розовые": ["pink", "розов", "розовая", "розовый"],
        "желтые": ["yellow", "желт", "желтая", "желтый"],
        "синие": ["blue", "син", "синяя", "синий"],
        "оранжевые": ["orange", "оранж", "оранжевая", "оранжевый"],
        "фиолетовые": ["purple", "фиолет", "фиолетовая", "фиолетовый"],
        "бордовые": ["burgundy", "бордов", "бордовая", "бордовый"],
        "персиковые": ["peach", "персиков", "персиковая", "персиковый"],
    }

    # Маппинг типов цветов (русский -> английский и варианты)
    flower_keywords = {
        "розы": ["rose", "roses", "роз", "роза"],
        "гвоздики": ["carnation", "carnations", "гвоздик", "гвоздика"],
        "герберы": ["gerbera", "gerberas", "гербер", "гербера"],
        "ромашки": ["daisy", "daisies", "ромашк", "ромашка"],
        "васильки": ["cornflower", "cornflowers", "василек", "васильк"],
        "тюльпаны": ["tulip", "tulips", "тюльпан", "тюльпан"],
        "хризантемы": ["chrysanthemum", "chrysanthemums", "хризантем", "хризантема"],
        "пионы": ["peony", "peonies", "пион", "пиона"],
        "лилии": ["lily", "lilies", "лили", "лилия"],
        "ирисы": ["iris", "irises", "ирис", "ириса"],
        "орхидеи": ["orchid", "orchids", "орхиде", "орхидея"],
        "альстромерии": ["alstroemeria", "альстром", "альстромерия"],
        "фрезии": ["freesia", "фрези", "фрезия"],
        "астры": ["aster", "asters", "астр", "астра"],
        "гладиолусы": ["gladiolus", "гладиолус", "гладиолуса"],
        "эустомы": ["eustoma", "эустом", "эустома"],
    }

    # Извлекаем цвет и тип цветка из названия
    found_color_keywords = []
    found_flower_keywords = []

    for ru_color, en_variants in color_keywords.items():
        if ru_color in normalized:
            found_color_keywords.extend(en_variants)
            break

    for ru_flower, en_variants in flower_keywords.items():
        if ru_flower in normalized:
            found_flower_keywords.extend(en_variants)
            break

    # Если не нашли цвет или тип, пробуем найти по частичному совпадению
    if not found_color_keywords:
        for ru_color, en_variants in color_keywords.items():
            if any(
                ru_color.startswith(word) or word.startswith(ru_color)
                for word in normalized.split()
            ):
                found_color_keywords.extend(en_variants)
                break

    if not found_flower_keywords:
        for ru_flower, en_variants in flower_keywords.items():
            if any(
                ru_flower.startswith(word) or word.startswith(ru_flower)
                for word in normalized.split()
            ):
                found_flower_keywords.extend(en_variants)
                break

    # Если это смешанный букет
    if "смешанный букет" in normalized or "букет" in normalized:
        found_flower_keywords.extend(["bouquet", "flowers", "букет"])

    if not found_flower_keywords:
        logger.warning(f"  ⚠ Не удалось определить тип цветка для '{flower_name}'")
        return None

    # Ищем файлы с максимальным совпадением
    best_matches = []

    for img_file in image_files:
        # Очищаем имя файла от timestamp и хешей
        img_name_clean = img_file.stem.lower()
        img_name_clean = re.sub(r"_\d+$", "", img_name_clean)  # убираем timestamp
        img_name_clean = re.sub(
            r"_[a-zA-Z0-9]{8,}$", "", img_name_clean
        )  # убираем хеши

        score = 0
        matched_keywords = []

        # Проверяем совпадения по цвету
        for color_kw in found_color_keywords:
            if color_kw in img_name_clean:
                score += 3  # Цвет важен
                matched_keywords.append(color_kw)

        # Проверяем совпадения по типу цветка
        for flower_kw in found_flower_keywords:
            if flower_kw in img_name_clean:
                score += 5  # Тип цветка очень важен
                matched_keywords.append(flower_kw)

        # Бонус за точное совпадение названия
        if normalized.replace(" ", "_") in img_name_clean:
            score += 10

        if score > 0:
            best_matches.append((img_file, score, matched_keywords))

    if not best_matches:
        return None

    # Сортируем по score (лучшие совпадения первыми)
    best_matches.sort(key=lambda x: x[1], reverse=True)

    # Возвращаем лучшее совпадение
    best_file, best_score, matched = best_matches[0]

    matched_str = ", ".join(matched[:3])
    logger.info(
        f"  Найдено: {best_file.name} (score: {best_score}, "
        f"совпадения: {matched_str})"
    )

    return best_file


def load_images_from_local():
    """Загружает изображения из локальной папки"""
    flowers = Flower.objects.all()
    media_path = Path(settings.MEDIA_ROOT) / "flowers"

    if not media_path.exists():
        logger.error(f"❌ Папка {media_path} не существует!")
        return

    # Загружаем все изображения
    image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
    logger.info("=" * 80)
    logger.info(f"Найдено {len(image_files)} локальных изображений в {media_path}")
    logger.info("=" * 80)
    logger.info(f"\nНачинаем обработку {flowers.count()} цветов...\n")

    if len(image_files) == 0:
        logger.error("❌ Нет изображений в папке!")
        return

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            # Ищем подходящее изображение
            matching_image = find_best_local_image(flower.name, image_files)

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

            # Сохраняем новое с timestamp для обхода кэша
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


if __name__ == "__main__":
    load_images_from_local()
