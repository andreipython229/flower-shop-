"""
Скрипт для проверки Unsplash API ключа
"""

import sys

import requests


def test_unsplash_key(api_key):
    """Проверяет валидность Unsplash API ключа"""
    if not api_key:
        print("❌ Ключ не указан!")
        return False

    print(f"Проверяю ключ: {api_key[:20]}...")
    print(f"Длина ключа: {len(api_key)} символов")
    print()

    try:
        headers = {"Authorization": f"Client-ID {api_key}"}

        # Тестовый запрос
        test_url = "https://api.unsplash.com/search/photos"
        params = {"query": "roses", "per_page": 1}

        print("Отправляю запрос к Unsplash API...")
        response = requests.get(test_url, headers=headers, params=params, timeout=10)

        print(f"Статус ответа: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                photo = data["results"][0]
                print("✅ КЛЮЧ ВАЛИДЕН!")
                image_url = photo.get("urls", {}).get("small", "N/A")[:60]
                print(f"   Найдено изображение: {image_url}...")
                return True
            else:
                print("⚠ Ключ работает, но нет результатов")
                return True
        elif response.status_code == 401:
            print("❌ КЛЮЧ НЕВАЛИДЕН (401 Unauthorized)")
            print()
            print("Возможные причины:")
            print("1. Ключ скопирован неправильно (проверь пробелы)")
            print("2. Ключ истек или был удален")
            print(
                "3. Нужно создать новое приложение на https://unsplash.com/developers"
            )
            return False
        else:
            print(f"⚠ Неожиданный статус: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ПРОВЕРКА UNSPLASH API КЛЮЧА")
    print("=" * 60)
    print()

    # Пробуем получить ключ из аргументов или переменной окружения
    if len(sys.argv) > 1:
        key = sys.argv[1]
    else:
        import os

        key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
        if not key:
            print("Использование:")
            print("  python test_unsplash_key.py ТВОЙ_КЛЮЧ")
            print("  или")
            print("  set UNSPLASH_ACCESS_KEY=ТВОЙ_КЛЮЧ")
            print("  python test_unsplash_key.py")
            print()
            key = input(
                "Введи ключ для проверки (или нажми Enter для выхода): "
            ).strip()

    if not key:
        print("Выход...")
        sys.exit(0)

    print()
    result = test_unsplash_key(key)
    print()

    if result:
        print("=" * 60)
        print("✅ Ключ работает! Можно использовать:")
        print(f"   set UNSPLASH_ACCESS_KEY={key}")
        print("   python load_images_with_unsplash_new_key.py")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Ключ не работает. Получи новый на https://unsplash.com/developers")
        print("=" * 60)
