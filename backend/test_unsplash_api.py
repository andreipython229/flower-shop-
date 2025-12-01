"""
Тест Unsplash API - проверяем, работает ли API ключ
"""

import os

import requests

UNSPLASH_ACCESS_KEY = os.environ.get(
    "UNSPLASH_ACCESS_KEY", "YIjTAjb14kWataGu6LAbCvgheBU1r7pM1R0u98tR9nQ"
).strip()
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def test_unsplash():
    """Тестирует Unsplash API"""
    print("=" * 60)
    print("ТЕСТ UNSPLASH API")
    print("=" * 60)
    print(f"API Key: {UNSPLASH_ACCESS_KEY[:20]}...")
    print(f"API URL: {UNSPLASH_API_URL}")
    print()

    # Тестовый запрос
    test_query = "red roses bouquet"
    print(f"Тестовый запрос: '{test_query}'")

    try:
        params = {"query": test_query, "per_page": 1, "client_id": UNSPLASH_ACCESS_KEY}

        print("Отправляем запрос...")
        response = requests.get(UNSPLASH_API_URL, params=params, timeout=10)

        print(f"Статус код: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                image_url = data["results"][0]["urls"]["regular"]
                print("✓ УСПЕХ! Получен URL изображения:")
                print(f"  {image_url}")
                return True
            else:
                print("⚠ API вернул пустой результат")
                return False
        else:
            print(f"✗ ОШИБКА! Статус код: {response.status_code}")
            print(f"  Ответ: {response.text[:200]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ ОШИБКА ЗАПРОСА: {e}")
        return False
    except Exception as e:
        print(f"✗ ОШИБКА: {e}")
        return False


if __name__ == "__main__":
    test_unsplash()
