"""
Проверка исходных файлов, которые использовал скрипт
"""

import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.conf import settings

media_path = Path(settings.MEDIA_ROOT) / "flowers"

# Файлы, которые использовал скрипт для проблемных цветов
source_files = {
    "Белые розы (35 шт)": "Белые_розы_11_шт.jpg",
    "Красные розы (35 шт)": "Красные_розы.jpg",
    "Белые фрезии (25 шт)": "Белые_фрезии_15_шт.jpg",
    "Желтые альстромерии (25 шт)": "Желтые_альстромерии_15_шт.jpg",
}

print("=" * 80)
print("ПРОВЕРКА ИСХОДНЫХ ФАЙЛОВ, КОТОРЫЕ ИСПОЛЬЗОВАЛ СКРИПТ")
print("=" * 80)

for flower_name, source_file in source_files.items():
    file_path = media_path / source_file
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"\n{flower_name}:")
        print(f"  Исходный файл: {source_file}")
        print(f"  Размер: {size:,} байт")
        print("  Существует: ✓")

        # Проверяем, есть ли другие файлы с похожими названиями
        similar_files = []
        for f in media_path.glob("*.jpg"):
            if (
                "белые" in source_file.lower()
                and "бел" in f.stem.lower()
                and "роз" in f.stem.lower()
            ):
                if f.name != source_file:
                    similar_files.append(f.name)
            elif (
                "красные" in source_file.lower()
                and "красн" in f.stem.lower()
                and "роз" in f.stem.lower()
            ):
                if f.name != source_file:
                    similar_files.append(f.name)
            elif (
                "белые" in source_file.lower()
                and "бел" in f.stem.lower()
                and "фрези" in f.stem.lower()
            ):
                if f.name != source_file:
                    similar_files.append(f.name)
            elif (
                "желтые" in source_file.lower()
                and "желт" in f.stem.lower()
                and "альстром" in f.stem.lower()
            ):
                if f.name != source_file:
                    similar_files.append(f.name)

        if similar_files:
            print(f"  Похожие файлы: {', '.join(similar_files[:3])}")
    else:
        print(f"\n{flower_name}:")
        print(f"  Исходный файл: {source_file}")
        print("  ✗ НЕ НАЙДЕН!")

print("\n" + "=" * 80)
print(
    "ВЫВОД: Возможно, файлы с правильными названиями содержат неправильные изображения."
)
print("Нужно либо:")
print("1. Использовать внешний источник (Unsplash/Pexels) с правильными изображениями")
print("2. Или проверить содержимое файлов вручную")
print("=" * 80)
