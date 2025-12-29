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
                    old_url = flower.image_url
                    # ВСЕГДА обновляем image_url из маппинга (принудительно)
                    flower.image_url = image_url
                    flower.save()
                    updated += 1
                    if old_url != image_url:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Обновлён: {flower.name}\n"
                                f"  Старый URL: {old_url[:80]}...\n"
                                f"  Новый URL: {image_url[:80]}..."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Подтверждён: {flower.name} (URL уже правильный)"
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ Цветок не найден в базе: {flower_name}"
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Ошибка для {flower_name}: {e}")
                )
                import traceback
                self.stdout.write(traceback.format_exc())

        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"Обновлено цветов: {updated} из {total}")
        )
        self.stdout.write("=" * 60)

