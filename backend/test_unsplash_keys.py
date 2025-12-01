"""
Тест разных способов использования Unsplash API ключей
"""

import requests

ACCESS_KEY = "YIjTAjb14kWataGu6LAbCvgheBU1r7pM1R0u98tR9nQ"
SECRET_KEY = "0t10cG_7VzrJPatG9BiIFfN3DcHrKJKe7SLjG43QRWE"
API_URL = "https://api.unsplash.com/search/photos"

print("=" * 60)
print("ТЕСТ UNSPLASH API КЛЮЧЕЙ")
print("=" * 60)

# Тест 1: Access Key как client_id (текущий способ)
print("\n1. Тест с Access Key как client_id:")
try:
    params = {"query": "red roses", "per_page": 1, "client_id": ACCESS_KEY}
    response = requests.get(API_URL, params=params, timeout=10)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            print(
                f"   ✓ РАБОТАЕТ! URL: {data['results'][0]['urls']['regular'][:50]}..."
            )
        else:
            print("   ⚠ Пустой результат")
    else:
        print(f"   ✗ Ошибка: {response.text[:100]}")
except Exception as e:
    print(f"   ✗ Ошибка: {e}")

# Тест 2: Access Key в заголовке Authorization
print("\n2. Тест с Access Key в заголовке Authorization:")
try:
    headers = {"Authorization": f"Client-ID {ACCESS_KEY}"}
    params = {"query": "red roses", "per_page": 1}
    response = requests.get(API_URL, headers=headers, params=params, timeout=10)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            print(
                f"   ✓ РАБОТАЕТ! URL: {data['results'][0]['urls']['regular'][:50]}..."
            )
        else:
            print("   ⚠ Пустой результат")
    else:
        print(f"   ✗ Ошибка: {response.text[:100]}")
except Exception as e:
    print(f"   ✗ Ошибка: {e}")

# Тест 3: Secret Key (маловероятно, но проверим)
print("\n3. Тест с Secret Key:")
try:
    params = {"query": "red roses", "per_page": 1, "client_id": SECRET_KEY}
    response = requests.get(API_URL, params=params, timeout=10)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            print(
                f"   ✓ РАБОТАЕТ! URL: {data['results'][0]['urls']['regular'][:50]}..."
            )
        else:
            print("   ⚠ Пустой результат")
    else:
        print(f"   ✗ Ошибка: {response.text[:100]}")
except Exception as e:
    print(f"   ✗ Ошибка: {e}")

print("\n" + "=" * 60)
