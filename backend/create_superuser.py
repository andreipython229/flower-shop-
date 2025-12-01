import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Создаем суперпользователя если его нет
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123")
    print("Суперпользователь создан:")
    print("Username: admin")
    print("Password: admin123")
else:
    print("Суперпользователь уже существует")
