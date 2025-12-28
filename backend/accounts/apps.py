from django.apps import AppConfig
from django.core.management import call_command
import os


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Применяем миграции при старте приложения
        # (если DATABASE_URL установлен - значит production)
        if os.environ.get("DATABASE_URL") and not os.environ.get(
            "SKIP_MIGRATIONS"
        ):
            try:
                print("=" * 60)
                print("Applying migrations on startup...")
                print("=" * 60)
                call_command("migrate", verbosity=2, interactive=False)
                print("=" * 60)
                print("Migrations completed!")
                print("=" * 60)

                # Проверяем, есть ли цветы в базе, если меньше 100 - запускаем парсинг
                try:
                    from flowers.models import Flower

                    flower_count = Flower.objects.count()
                    if flower_count < 100:
                        print("=" * 60)
                        print(
                            f"Found only {flower_count} flowers in database. "
                            f"Starting parsing..."
                        )
                        print("=" * 60)
                        # Очищаем базу перед парсингом, если цветов мало
                        if flower_count > 0:
                            Flower.objects.all().delete()
                            print("Database cleared before parsing")
                        call_command("parse_flowers", verbosity=2)
                        final_count = Flower.objects.count()
                        print("=" * 60)
                        print(f"Flowers parsing completed! Total: {final_count}")
                        print("=" * 60)
                    else:
                        print(f"✓ Found {flower_count} flowers in database")
                        # Проверяем, есть ли цветы без image_url
                        flowers_without_image = Flower.objects.filter(
                            image_url__isnull=True
                        ).count()
                        if flowers_without_image > 0:
                            print("=" * 60)
                            print(
                                f"Found {flowers_without_image} flowers without image_url. "
                                f"Updating images..."
                            )
                            print("=" * 60)
                            call_command("update_flower_images", verbosity=2)
                            print("=" * 60)
                            print("Image update completed!")
                            print("=" * 60)
                except Exception as e:
                    print(f"Error checking/parsing flowers: {e}")

            except Exception as e:
                print(f"Error applying migrations: {e}")
