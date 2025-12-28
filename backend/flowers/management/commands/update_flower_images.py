from django.core.management.base import BaseCommand
from flowers.models import Flower
from flowers.parsers import FLOWER_IMAGE_MAP


class Command(BaseCommand):
    help = "Обновляет image_url для всех цветов из маппинга"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("Обновление image_url для цветов..."))
        self.stdout.write("=" * 60)

        # Обновляем все цветы, которые есть в маппинге
        total = 0
        updated = 0

        for flower_name, image_url in FLOWER_IMAGE_MAP.items():
            try:
                flower = Flower.objects.filter(name=flower_name).first()
                if flower:
                    total += 1
                    # Обновляем image_url, даже если он уже есть
                    if flower.image_url != image_url:
                        flower.image_url = image_url
                        flower.save()
                        updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Обновлён: {flower.name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"○ Уже обновлён: {flower.name}")
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Ошибка для {flower_name}: {e}")
                )

        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"Обновлено цветов: {updated} из {total}")
        )
        self.stdout.write("=" * 60)

