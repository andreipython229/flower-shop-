import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Проверяем сколько вариантов "Розовые орхидеи"
orchids = Flower.objects.filter(name__icontains="Розовые орхидеи")
print(f"Найдено вариантов 'Розовые орхидеи': {orchids.count()}")
for orchid in orchids:
    print(f"  - {orchid.name}")
