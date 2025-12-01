"""
Проверка реального API ответа через HTTP запрос
"""

import requests


def check_real_api():
    """Проверяет реальный API ответ"""
    api_url = "http://localhost:8000/api/flowers/"

    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()

            print("=" * 80)
            print("ПРОВЕРКА РЕАЛЬНОГО API ОТВЕТА")
            print("=" * 80)

            # Проверяем первые 10 цветов
            for flower in data[:10]:
                print(f"\n{flower['name']}:")
                print(f"  image_url: {flower.get('image_url', 'НЕТ')}")
                print(f"  image: {flower.get('image', 'НЕТ')}")

                # Проверяем, что image_url - это полный URL
                image_url = flower.get("image_url")
                if image_url:
                    if image_url.startswith("http"):
                        print("  ✓ Полный URL")
                    else:
                        print(f"  ✗ Относительный путь: {image_url}")
                else:
                    print("  ✗ НЕТ image_url")
        else:
            print(f"Ошибка API: статус {response.status_code}")
            print("Убедитесь, что Django сервер запущен на http://localhost:8000")
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения к API")
        print("Убедитесь, что Django сервер запущен: python manage.py runserver")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    check_real_api()
