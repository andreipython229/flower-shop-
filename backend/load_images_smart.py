"""
Умный скрипт для загрузки изображений:
1. Пробует использовать Unsplash API с ключом (если есть)
2. Если ключа нет - использует локальные изображения из media/flowers/
"""

import os
import re
import time
from pathlib import Path

import django
import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# Проверяем Unsplash API ключ
def get_unsplash_key():
    """Получает Unsplash API ключ из переменных окружения или .env файла"""
    # Проверяем переменные окружения
    key = os.environ.get("UNSPLASH_ACCESS_KEY") or os.environ.get("UNSPLASH_API_KEY")

    if key:
        return key

    # Проверяем .env файлы
    env_files = [".env", ".env.local", "backend/.env", "../.env"]
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if (
                            "UNSPLASH" in line.upper()
                            and "KEY" in line.upper()
                            and "=" in line
                        ):
                            key_part = line.split("=")[1].strip().strip('"').strip("'")
                            if key_part:
                                return key_part
            except Exception:
                pass

    return None


def normalize_flower_name(name):
    """Нормализует название цветка"""
    clean = re.sub(r"\s*\(\d+\s*шт\)", "", name.lower()).strip()
    clean = clean.replace('"', "").replace("«", "").replace("»", "")
    clean = re.sub(r"\s+", " ", clean)
    return clean


def get_english_search_query(flower_name):
    """Преобразует русское название в английский поисковый запрос для Unsplash"""
    normalized = normalize_flower_name(flower_name)

    color_map = {
        "красные": "red",
        "белые": "white",
        "розовые": "pink",
        "желтые": "yellow",
        "синие": "blue",
        "оранжевые": "orange",
        "фиолетовые": "purple",
        "бордовые": "burgundy",
        "персиковые": "peach",
    }

    flower_map = {
        "розы": "roses",
        "гвоздики": "carnations",
        "герберы": "gerbera",
        "ромашки": "daisies",
        "васильки": "cornflowers",
        "тюльпаны": "tulips",
        "хризантемы": "chrysanthemums",
        "пионы": "peonies",
        "лилии": "lilies",
        "ирисы": "irises",
        "орхидеи": "orchids",
        "альстромерии": "alstroemeria",
        "фрезии": "freesia",
        "астры": "asters",
        "гладиолусы": "gladiolus",
        "эустомы": "eustoma",
    }

    found_color = None
    found_flower = None

    for ru, en in color_map.items():
        if ru in normalized:
            found_color = en
            break

    for ru, en in flower_map.items():
        if ru in normalized:
            found_flower = en
            break

    if found_color and found_flower:
        return f"{found_color} {found_flower} bouquet"
    elif found_flower:
        return f"{found_flower} bouquet"
    elif "смешанный букет" in normalized or "букет" in normalized:
        return "flower bouquet"
    else:
        return "flowers"


def get_unsplash_image(api_key, search_query):
    """Получает изображение из Unsplash API"""
    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        # Ищем изображение по запросу
        search_url = "https://api.unsplash.com/search/photos"
        params = {"query": search_query, "per_page": 1, "orientation": "landscape"}

        response = requests.get(search_url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                photo = data["results"][0]
                # Возвращаем URL изображения нужного размера
                return photo.get("urls", {}).get("regular") or photo.get(
                    "urls", {}
                ).get("small")
        elif response.status_code == 401:
            logger.warning("⚠ Unsplash API ключ невалиден (401)")
            return None
        else:
            logger.warning(f"⚠ Unsplash API вернул статус {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"✗ Ошибка при запросе к Unsplash API: {e}")
        return None


def find_local_image(flower_name, image_files):
    """Находит локальное изображение для цветка"""
    normalized = normalize_flower_name(flower_name)

    # Ищем файлы, которые содержат название цветка
    # Приоритет: точное совпадение > частичное совпадение
    exact_matches = []
    partial_matches = []

    for img_file in image_files:
        img_name_lower = img_file.stem.lower()

        # Убираем timestamp и хеши из имени файла для сравнения
        clean_img_name = re.sub(r"_\d+$", "", img_name_lower)  # убираем timestamp
        clean_img_name = re.sub(
            r"_[a-zA-Z0-9]{8,}$", "", clean_img_name
        )  # убираем хеши

        # Проверяем точное совпадение ключевых слов
        flower_words = normalized.split()
        img_words = clean_img_name.split("_")

        # Считаем совпадения
        matches = sum(
            1
            for word in flower_words
            if any(
                word in img_word or img_word in word
                for img_word in img_words
                if len(word) > 2
            )
        )

        if matches >= 2:  # Минимум 2 совпадения
            if matches == len(flower_words):  # Все слова совпали
                exact_matches.append((img_file, matches))
            else:
                partial_matches.append((img_file, matches))

    # Сортируем по количеству совпадений
    if exact_matches:
        exact_matches.sort(key=lambda x: x[1], reverse=True)
        return exact_matches[0][0]
    elif partial_matches:
        partial_matches.sort(key=lambda x: x[1], reverse=True)
        return partial_matches[0][0]

    return None


def validate_unsplash_key(api_key):
    """Проверяет валидность Unsplash API ключа"""
    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        # Тестовый запрос
        test_url = "https://api.unsplash.com/search/photos"
        params = {"query": "roses", "per_page": 1}
        response = requests.get(test_url, headers=headers, params=params, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def load_images():
    """Главная функция загрузки изображений"""
    flowers = Flower.objects.all()

    # Проверяем наличие Unsplash API ключа
    unsplash_key = get_unsplash_key()
    use_unsplash = False

    if unsplash_key:
        logger.info("=" * 80)
        logger.info("ПРОВЕРКА UNSPLASH API КЛЮЧА")
        logger.info("=" * 80)
        logger.info(f"Ключ найден: {unsplash_key[:20]}...")

        # Проверяем валидность ключа
        if validate_unsplash_key(unsplash_key):
            logger.info("✓ Ключ валиден, используем Unsplash API")
            use_unsplash = True
        else:
            logger.warning(
                "⚠ Ключ невалиден (401), переключаемся на локальные изображения"
            )
            use_unsplash = False

    if use_unsplash:
        logger.info("=" * 80)
        logger.info("ИСПОЛЬЗУЕМ UNSPLASH API С КЛЮЧОМ")
        logger.info("=" * 80)
    else:
        logger.info("=" * 80)
        logger.info("ИСПОЛЬЗУЕМ ЛОКАЛЬНЫЕ ИЗОБРАЖЕНИЯ ИЗ media/flowers/")
        logger.info("=" * 80)

        # Загружаем список локальных изображений
        media_path = Path(settings.MEDIA_ROOT) / "flowers"
        if not media_path.exists():
            logger.error(f"❌ Папка {media_path} не существует!")
            return

        image_files = list(media_path.glob("*.jpg")) + list(media_path.glob("*.jpeg"))
        logger.info(f"Найдено {len(image_files)} локальных изображений")

        if len(image_files) == 0:
            logger.error("❌ Нет локальных изображений!")
            return

    logger.info(f"\nНачинаем обработку {flowers.count()} цветов...\n")

    updated = 0
    skipped = 0
    failed = 0

    for flower in flowers:
        try:
            image_url = None
            local_image = None

            # Пробуем получить изображение
            if use_unsplash:
                search_query = get_english_search_query(flower.name)
                image_url = get_unsplash_image(unsplash_key, search_query)
                if not image_url:
                    logger.warning(
                        f"⚠ Не найдено изображение для '{flower.name}' "
                        f"(запрос: '{search_query}')"
                    )
                    skipped += 1
                    continue
            else:
                local_image = find_local_image(flower.name, image_files)
                if not local_image:
                    logger.warning(
                        f"⚠ Не найдено локальное изображение для '{flower.name}'"
                    )
                    skipped += 1
                    continue

            # Удаляем старое изображение
            if flower.image:
                try:
                    old_path = flower.image.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

            # Сохраняем новое изображение
            try:
                if use_unsplash and image_url:
                    # Скачиваем из Unsplash
                    response = requests.get(
                        image_url,
                        stream=True,
                        timeout=15,
                        headers={"User-Agent": "Mozilla/5.0"},
                    )
                    response.raise_for_status()

                    safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                    safe_name = re.sub(r"[-\s]+", "_", safe_name)
                    timestamp = int(time.time())
                    file_name = f"{safe_name}_{timestamp}.jpg"

                    image_content = ContentFile(response.content)
                    image_path = default_storage.save(
                        f"flowers/{file_name}", image_content
                    )

                    flower.image = image_path
                    flower.image_url = None
                    flower.save()

                    logger.info(f"✓ '{flower.name}' -> Unsplash ({search_query})")
                    updated += 1

                elif not use_unsplash and local_image:
                    # Используем локальное изображение
                    with open(local_image, "rb") as f:
                        safe_name = re.sub(r"[^\w\s-]", "", flower.name).strip()
                        safe_name = re.sub(r"[-\s]+", "_", safe_name)
                        timestamp = int(time.time())
                        file_name = f"{safe_name}_{timestamp}{local_image.suffix}"

                        flower.image.save(file_name, File(f), save=True)
                        flower.image_url = None
                        flower.save()

                        logger.info(f"✓ '{flower.name}' -> {local_image.name}")
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
    load_images()
