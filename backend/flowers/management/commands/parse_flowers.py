from django.core.management.base import BaseCommand
from flowers.parsers import FlowerParser


class Command(BaseCommand):
    help = "Парсинг и сохранение цветов в базу данных"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Начинаем парсинг цветов..."))
        self.stdout.write("=" * 60)

        parser = FlowerParser()
        flowers_data = parser.parse_flowers()
        parser.save_flowers(flowers_data)

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Парсинг цветов завершён!"))
        self.stdout.write("=" * 60)

