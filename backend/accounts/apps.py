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

                # Проверяем, есть ли цветы в базе, если нет - запускаем парсинг
                try:
                    from flowers.models import Flower

                    flower_count = Flower.objects.count()
                    if flower_count == 0:
                        print("=" * 60)
                        print("No flowers found in database. Starting parsing...")
                        print("=" * 60)
                        call_command("parse_flowers", verbosity=2)
                        print("=" * 60)
                        print("Flowers parsing completed!")
                        print("=" * 60)
                    else:
                        print(f"✓ Found {flower_count} flowers in database")
                except Exception as e:
                    print(f"Error checking/parsing flowers: {e}")

            except Exception as e:
                print(f"Error applying migrations: {e}")
