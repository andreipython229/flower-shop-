"""
Проверка реальных изображений по URL из Pexels
"""

from pathlib import Path

import requests

# Тестируем URL для проблемных цветов
test_urls = {
    "белые розы": ("https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"),
    "красные розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
    ),
    "белые фрезии": (
        "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
    ),
    "желтые альстромерии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
    ),
}

print("=" * 80)
print("ПРОВЕРКА URL ИЗ PEXELS - ЧТО РЕАЛЬНО СКАЧИВАЕТСЯ")
print("=" * 80)

# Скачиваем и сохраняем для проверки
for name, url in test_urls.items():
    try:
        print(f"\n{name}:")
        print(f"  URL: {url}")

        response = requests.get(
            url, stream=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"}
        )

        if response.status_code == 200:
            size = len(response.content)
            content_type = response.headers.get("Content-Type", "")
            print("  Статус: ✓ 200 OK")
            print(f"  Размер: {size:,} байт")
            print(f"  Тип: {content_type}")

            # Сохраняем для проверки
            safe_name = name.replace(" ", "_").replace("ы", "y")
            test_file = Path(f"test_{safe_name}.jpg")
            with open(test_file, "wb") as f:
                f.write(response.content)
            print(f"  Сохранено: {test_file} (для проверки)")
        else:
            print(f"  ✗ Ошибка: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Ошибка: {e}")

print("\n" + "=" * 80)
print("ВЫВОД: Проверь файлы test_*.jpg - что в них реально изображено")
print("Если изображения неправильные - нужно найти другие URL")
print("=" * 80)
