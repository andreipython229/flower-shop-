from django.core.management.base import BaseCommand
from flowers.models import Flower
from flowers.parsers import FlowerParser


class Command(BaseCommand):
    help = "Обновляет image_url для всех цветов без изображений"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Обновление image_url для цветов..."))
        self.stdout.write("=" * 60)

        parser = FlowerParser()
        flowers = Flower.objects.filter(image_url__isnull=True)
        total = flowers.count()
        self.stdout.write(f"Найдено цветов без image_url: {total}")

        updated = 0
        for flower in flowers:
            try:
                # Получаем image_url по названию
                image_url = parser._get_flower_image_url_by_name(flower.name)
                if not image_url:
                    search_query = f"{flower.name} bouquet"
                    image_url = parser._get_working_image_url(flower.name, search_query)

                if image_url:
                    flower.image_url = image_url
                    flower.save()
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Обновлён: {flower.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Не найден image_url: {flower.name}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Ошибка для {flower.name}: {e}")
                )

        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"Обновлено цветов: {updated} из {total}")
        )
        self.stdout.write("=" * 60)

