"""
Проверка реального содержимого изображений по URL из Pexels
"""

import requests


def verify_pexels_urls():
    """Проверяет, что изображения по URL действительно содержат правильные цветы"""

    # Тестовые URL из нашего маппинга
    test_urls = {
        "Красные розы": (
            "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        ),
        "Белые розы": (
            "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        ),
        "Розовые розы": (
            "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
        ),
        "Желтые розы": (
            "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        ),
        "Белые фрезии": (
            "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        ),
        "Желтые альстромерии": (
            "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
        ),
        "Розовые альстромерии": (
            "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        ),
        "Розовые орхидеи": (
            "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
        ),
        "Белые орхидеи": (
            "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
        ),
        "Фиолетовые ирисы": (
            "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
        ),
        "Синие ирисы": (
            "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
        ),
        "Розовые лилии": (
            "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
        ),
        "Белые лилии": (
            "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
        ),
        "Белые пионы": (
            "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
        ),
        "Розовые пионы": (
            "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
        ),
    }

    print("=" * 80)
    print("ПРОВЕРКА РЕАЛЬНОГО СОДЕРЖИМОГО ИЗОБРАЖЕНИЙ")
    print("=" * 80)
    print("\n⚠ ВНИМАНИЕ: Эта проверка только проверяет доступность URL.")
    print("Для проверки содержимого нужно открыть URL в браузере.\n")

    for name, url in test_urls.items():
        try:
            response = requests.head(
                url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "image" in content_type:
                    print(f"✓ {name}: URL доступен ({url[:60]}...)")
                    print(f"  Откройте в браузере для проверки: {url}")
                else:
                    print(f"✗ {name}: URL не является изображением")
            else:
                status = response.status_code
                print(f"✗ {name}: URL недоступен (статус {status})")
        except Exception as e:
            print(f"✗ {name}: Ошибка при проверке: {e}")

    print("\n" + "=" * 80)
    print("РЕКОМЕНДАЦИЯ:")
    print("=" * 80)
    msg = (
        "Проблема в том, что URL из Pexels могут не содержать "
        "правильные изображения."
    )
    print(msg)
    print("Нужно либо:")
    print("1. Проверить каждый URL вручную в браузере")
    print("2. Использовать другой источник изображений")
    print("3. Загрузить правильные изображения локально")


if __name__ == "__main__":
    verify_pexels_urls()
