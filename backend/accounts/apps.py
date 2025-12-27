import os

from django.apps import AppConfig
from django.core.management import call_command


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Применяем миграции при старте приложения
        # (если DATABASE_URL установлен - значит production)
        if os.environ.get("DATABASE_URL") and not os.environ.get("SKIP_MIGRATIONS"):
            try:
                print("=" * 60)
                print("Applying migrations on startup...")
                print("=" * 60)
                call_command("migrate", verbosity=2, interactive=False)
                print("=" * 60)
                print("Migrations completed!")
                print("=" * 60)
            except Exception as e:
                print(f"Error applying migrations: {e}")
