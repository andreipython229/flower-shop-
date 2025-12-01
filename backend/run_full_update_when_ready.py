"""
Скрипт для обновления всех цветов через Unsplash API
Проверяет лимит перед запуском
"""

import os
import sys

import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()


def check_limit():
    """Проверяет лимит Unsplash API"""
    if not UNSPLASH_ACCESS_KEY:
        logger.error("❌ UNSPLASH_ACCESS_KEY не установлен!")
        return False

    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

    params = {"query": "roses", "per_page": 1}

    try:
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            headers=headers,
            params=params,
            timeout=10,
        )

        if "X-Ratelimit-Remaining" in response.headers:
            remaining = int(response.headers["X-Ratelimit-Remaining"])
            limit = int(response.headers.get("X-Ratelimit-Limit", "50"))

            logger.info(f"📊 Осталось запросов: {remaining} из {limit}")

            if remaining > 0:
                return True
            else:
                logger.warning("⏰ Лимит исчерпан! Нужно подождать.")
                if "X-Ratelimit-Reset" in response.headers:
                    reset_time = int(response.headers["X-Ratelimit-Reset"])
                    import datetime

                    reset_datetime = datetime.datetime.fromtimestamp(reset_time)
                    now = datetime.datetime.now()
                    wait_time = reset_datetime - now

                    if wait_time.total_seconds() > 0:
                        minutes = int(wait_time.total_seconds() / 60)
                        logger.info(
                            f"⏰ Лимит сбросится через: {minutes} минут (в {
        reset_datetime.strftime('%H:%M:%S')})"
                        )
                return False
        else:
            logger.warning("⚠️  Информация о лимите не найдена")
            return True
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке лимита: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("ПРОВЕРКА ЛИМИТА И ЗАПУСК ОБНОВЛЕНИЯ")
    logger.info("=" * 80)

    if not check_limit():
        logger.error("❌ Нельзя запускать обновление - лимит исчерпан!")
        sys.exit(1)

    logger.info("✅ Лимит позволяет запустить обновление!")
    logger.info("")
    logger.info("Запускаю полное обновление всех цветов...")
    logger.info(
        "(Используй load_images_with_unsplash_new_key.py для полного обновления)"
    )
    logger.info("")
    logger.info("Команда для запуска:")
    logger.info(
        "$env:UNSPLASH_ACCESS_KEY='твой_ключ'; python load_images_with_unsplash_new_key.py"
    )
