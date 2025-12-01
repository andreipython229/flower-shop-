import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Проверяем сколько вариантов "Розовые гвоздики"
carnations = Flower.objects.filter(name__icontains="Розовые гвоздики")
print(f"Найдено вариантов 'Розовые гвоздики': {carnations.count()}")
for carnation in carnations:
    print(f"  - {carnation.name}")
