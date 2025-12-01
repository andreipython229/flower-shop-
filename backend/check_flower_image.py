import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

# Проверяем несколько цветов
flowers_to_check = ["Белые розы", "Красные розы", "Желтые альстромерии", "Белые фрезии"]

for name_part in flowers_to_check:
    flower = Flower.objects.filter(name__icontains=name_part).first()
    if flower:
        print(f"\n{flower.name}:")
        if flower.image:
            print(f"  Изображение: {flower.image.name}")
            print(f"  URL: {flower.image.url}")
        else:
            print("  Нет изображения")
