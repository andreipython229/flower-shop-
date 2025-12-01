"""
Удаляет все изображения из базы данных, чтобы использовать placeholder
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.core.files.storage import default_storage

from flowers.models import Flower


def clear_all_images():
    """Удаляет все изображения из базы данных"""
    flowers = Flower.objects.all()

    print("=" * 80)
    print("УДАЛЕНИЕ ВСЕХ ИЗОБРАЖЕНИЙ ИЗ БАЗЫ ДАННЫХ")
    print("=" * 80)

    deleted_count = 0

    for flower in flowers:
        if flower.image:
            try:
                # Удаляем файл
                if default_storage.exists(flower.image.path):
                    default_storage.delete(flower.image.path)
                    print(f"✓ Удален файл: {flower.image.path}")

                # Очищаем поле в базе
                flower.image = None
                flower.image_url = None
                flower.save()
                deleted_count += 1
            except Exception as e:
                print(f"✗ Ошибка при удалении изображения для '{flower.name}': {e}")

    print("=" * 80)
    print(f"Удалено изображений: {deleted_count}")
    print("Теперь все цветы будут использовать placeholder")
    print("=" * 80)


if __name__ == "__main__":
    clear_all_images()
