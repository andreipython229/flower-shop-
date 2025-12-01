"""
Проверка источников файлов - откуда они были скопированы
"""

import hashlib
import os
from pathlib import Path

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.models import Flower

print("=" * 80)
print("ПРОВЕРКА ИСТОЧНИКОВ ФАЙЛОВ - ОТКУДА ОНИ БЫЛИ СКОПИРОВАНЫ")
print("=" * 80)

# Проверяем проблемные цветы
problem_flowers = [
    "Белые розы (35 шт)",
    "Красные розы (35 шт)",
    "Белые фрезии (25 шт)",
    "Желтые альстромерии (25 шт)",
]

media_path = Path(settings.MEDIA_ROOT) / "flowers"

for flower_name in problem_flowers:
    try:
        flower = Flower.objects.get(name=flower_name)
        if flower.image:
            current_file = Path(flower.image.path)

            print(f"\n{flower_name}:")
            print(f"  Текущий файл: {current_file.name}")

            if current_file.exists():
                # Вычисляем хеш файла
                with open(current_file, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                file_size = current_file.stat().st_size

                print(f"  Размер: {file_size:,} байт")
                print(f"  MD5: {file_hash[:16]}...")

                # Ищем файлы с таким же хешем (одинаковые файлы)
                same_hash_files = []
                for img_file in media_path.glob("*.jpg"):
                    if img_file != current_file:
                        try:
                            with open(img_file, "rb") as f:
                                other_hash = hashlib.md5(f.read()).hexdigest()
                            if other_hash == file_hash:
                                same_hash_files.append(img_file.name)
                        except Exception:
                            pass

                if same_hash_files:
                    print("  ⚠ ОДИНАКОВЫЕ ФАЙЛЫ (по содержимому):")
                    for f in same_hash_files[:5]:
                        print(f"     - {f}")
                else:
                    print("  ✓ Уникальный файл (по содержимому)")

                # Проверяем, есть ли исходный файл с похожим названием
                # (который мог быть использован как источник)
                source_candidates = []
                for img_file in media_path.glob("*.jpg"):
                    if img_file != current_file:
                        # Ищем файлы, которые могли быть источником
                        # (без timestamp в конце)
                        img_name_clean = img_file.stem
                        img_name_clean = (
                            img_name_clean.rsplit("_", 1)[0]
                            if "_" in img_name_clean
                            else img_name_clean
                        )

                        current_name_clean = (
                            current_file.stem.rsplit("_", 1)[0]
                            if "_" in current_file.stem
                            else current_file.stem
                        )

                        # Если имена похожи (без количества и timestamp)
                        if img_name_clean.lower() == current_name_clean.lower():
                            source_candidates.append(img_file.name)

                if source_candidates:
                    print("  Возможные исходные файлы:")
                    for f in source_candidates[:3]:
                        print(f"     - {f}")
            else:
                print("  ✗ Файл не существует!")

    except Flower.DoesNotExist:
        print(f"\n{flower_name}: ✗ Не найден")
    except Exception as e:
        print(f"\n{flower_name}: ✗ Ошибка - {e}")

print("\n" + "=" * 80)
print("ВЫВОД: Если файлы одинаковые по содержимому - значит они были скопированы")
print("из одного источника, и нужно найти правильные исходные файлы")
print("=" * 80)
