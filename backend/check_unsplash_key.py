"""
Проверка Unsplash API ключа
"""

import os

import requests

# Проверяем переменные окружения
unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY") or os.environ.get(
    "UNSPLASH_API_KEY"
)

print("=" * 80)
print("ПРОВЕРКА UNSPLASH API КЛЮЧА")
print("=" * 80)

if not unsplash_key:
    print("❌ Ключ не найден в переменных окружения")
    print("\nПроверяем файлы .env...")

    # Проверяем .env файл
    env_files = [".env", ".env.local", "backend/.env"]
    found_key = None

    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"  Найден файл: {env_file}")
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "UNSPLASH" in line.upper() and "KEY" in line.upper():
                            key_part = line.split("=")[1].strip() if "=" in line else ""
                            if key_part:
                                found_key = key_part
                                print(f"  ✓ Найден ключ: {key_part[:20]}...")
                                break
            except Exception as e:
                print(f"  ✗ Ошибка чтения: {e}")

    if not found_key:
        print("\n❌ Ключ не найден ни в переменных окружения, ни в .env файлах")
        print("\nДля получения ключа:")
        print("1. Зарегистрируйся на https://unsplash.com/developers")
        print("2. Создай новое приложение")
        print("3. Скопируй Access Key")
        print("4. Добавь в .env файл: UNSPLASH_ACCESS_KEY=твой_ключ")
    else:
        unsplash_key = found_key
else:
    print(f"✓ Ключ найден в переменных окружения: {unsplash_key[:20]}...")

# Проверяем валидность ключа
if unsplash_key:
    print("\n" + "=" * 80)
    print("ПРОВЕРКА ВАЛИДНОСТИ КЛЮЧА")
    print("=" * 80)

    try:
        # Тестовый запрос к Unsplash API
        headers = {"Authorization": f"Client-ID {unsplash_key}"}
        response = requests.get(
            "https://api.unsplash.com/photos/random?query=roses&count=1",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                photo = data[0]
                print("✓ Ключ ВАЛИДЕН!")
                print(
                    f"  Тестовое изображение: "
                    f"{photo.get('urls', {}).get('small', 'N/A')}"
                )
                print(f"  Автор: {photo.get('user', {}).get('name', 'N/A')}")
            else:
                print("⚠ Ключ работает, но ответ неожиданный")
        elif response.status_code == 401:
            print("❌ Ключ НЕВАЛИДЕН (401 Unauthorized)")
            print("   Проверь правильность ключа")
        else:
            print(f"⚠ Неожиданный статус: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при проверке ключа: {e}")
        print("   Проверь интернет-соединение")

print("\n" + "=" * 80)
