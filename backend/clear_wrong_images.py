"""
Скрипт для очистки неправильных изображений и использования placeholder'ов
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import logging

from flowers.models import Flower

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def clear_wrong_images():
    """Очищает все изображения, чтобы использовались placeholder'ы"""
    flowers = Flower.objects.all()

    logger.info(f"Очищаем изображения для {flowers.count()} цветов...")
    logger.info("После очистки будут использоваться placeholder'ы из фронтенда")

    cleared = 0
    errors = 0

    for flower in flowers:
        try:
            # Удаляем старое изображение, если оно есть
            if flower.image:
                try:
                    old_image_path = flower.image.path
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                except Exception as e:
                    logger.warning(
                        f"  Не удалось удалить файл для '{flower.name}': {e}"
                    )

            # Очищаем поле изображения
            flower.image = None
            flower.image_url = None
            flower.save()

            cleared += 1

        except Exception as e:
            logger.error(f"✗ Ошибка для '{flower.name}': {e}")
            errors += 1

    logger.info("\n" + "=" * 60)
    logger.info("Очистка завершена!")
    logger.info(f"Очищено: {cleared}")
    logger.info(f"Ошибок: {errors}")
    logger.info(f"Всего: {flowers.count()}")
    logger.info("\nТеперь все цветы будут использовать placeholder'ы из фронтенда")
    logger.info("Placeholder'ы выглядят как цветные круги с узором цветка")


if __name__ == "__main__":
    clear_wrong_images()
