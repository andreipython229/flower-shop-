"""
Проверка изображений в media/flowers/
"""

from pathlib import Path

media_path = Path("media/flowers")

if not media_path.exists():
    print("Папка media/flowers/ не существует!")
    exit(1)

# Получаем все изображения
jpg_files = list(media_path.glob("*.jpg"))
jpeg_files = list(media_path.glob("*.jpeg"))
all_files = jpg_files + jpeg_files

print("=" * 80)
print(f"Всего изображений: {len(all_files)}")
print("=" * 80)
print("\nПервые 20 файлов:")
print("-" * 80)

for i, file in enumerate(all_files[:20], 1):
    size = file.stat().st_size
    print(f"{i:2d}. {file.name} ({size:,} байт)")

if len(all_files) > 20:
    print(f"\n... и еще {len(all_files) - 20} файлов")

# Проверяем, есть ли файлы с названиями цветов
print("\n" + "=" * 80)
print("Поиск файлов с названиями цветов:")
print("-" * 80)

flower_keywords = [
    "розы",
    "фрезии",
    "альстромерии",
    "орхидеи",
    "ирисы",
    "лилии",
    "пионы",
    "хризантемы",
    "герберы",
    "гвоздики",
    "тюльпаны",
    "ромашки",
    "васильки",
]

found_by_keyword = {}
for keyword in flower_keywords:
    matching = [f for f in all_files if keyword.lower() in f.name.lower()]
    if matching:
        found_by_keyword[keyword] = len(matching)
        print(f"{keyword}: {len(matching)} файлов")

print("\n" + "=" * 80)
