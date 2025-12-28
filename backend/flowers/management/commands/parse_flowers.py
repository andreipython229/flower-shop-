from django.core.management.base import BaseCommand
from flowers.parsers import FlowerParser
from flowers.models import Flower


class Command(BaseCommand):
    help = "Парсинг и сохранение цветов в базу данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить базу данных перед парсингом",
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Начинаем парсинг цветов..."))
        self.stdout.write("=" * 60)

        # Проверяем количество цветов в базе
        current_count = Flower.objects.count()
        self.stdout.write(f"Текущее количество цветов в базе: {current_count}")

        # Очищаем базу, если указан флаг или если цветов меньше ожидаемого
        if options["clear"] or current_count < 100:
            self.stdout.write(
                self.style.WARNING("Очищаем базу данных перед парсингом...")
            )
            Flower.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("База данных очищена"))

        parser = FlowerParser()
        flowers_data = parser.parse_flowers()
        self.stdout.write(f"Найдено цветов для парсинга: {len(flowers_data)}")

        parser.save_flowers(flowers_data)

        final_count = Flower.objects.count()
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"Парсинг цветов завершён! Всего в базе: {final_count}")
        )
        self.stdout.write("=" * 60)

