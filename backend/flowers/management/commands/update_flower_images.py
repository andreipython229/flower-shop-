"""
Временный файл для исправления ошибки на Render.
Файл будет удалён после обновления кода на Render.
"""
from django.core.management.base import BaseCommand
from flowers.models import Flower


class Command(BaseCommand):
    help = "Обновление изображений цветов (исправленная версия)"

    def handle(self, *args, **options):
        """Исправленная версия - с проверкой на None"""
        self.stdout.write("Команда update_flower_images отключена.")
        self.stdout.write("Используйте FLOWER_IMAGE_MAP в parsers.py для изображений.")
        return

