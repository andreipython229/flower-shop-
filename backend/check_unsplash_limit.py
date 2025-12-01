"""
Проверяет лимит Unsplash API
"""

import os

import requests

UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()

if not UNSPLASH_ACCESS_KEY:
    print("❌ UNSPLASH_ACCESS_KEY не установлен!")
    print("Установите: $env:UNSPLASH_ACCESS_KEY='ваш_ключ'")
    exit(1)

headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

params = {"query": "roses", "per_page": 1}

print("🔍 Проверяю лимит Unsplash API...")
print(f"Ключ: {UNSPLASH_ACCESS_KEY[:20]}...")

try:
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        headers=headers,
        params=params,
        timeout=10,
    )

    print(f"\n📊 Статус ответа: {response.status_code}")

    # Проверяем заголовки с лимитами
    if "X-Ratelimit-Remaining" in response.headers:
        remaining = response.headers["X-Ratelimit-Remaining"]
        limit = response.headers.get("X-Ratelimit-Limit", "50")
        print(f"✅ Осталось запросов: {remaining} из {limit}")

        if int(remaining) > 0:
            print("✅ Можно запускать скрипт!")
        else:
            print("❌ Лимит исчерпан! Нужно подождать.")

            # Проверяем время сброса
            if "X-Ratelimit-Reset" in response.headers:
                reset_time = int(response.headers["X-Ratelimit-Reset"])
                import datetime

                reset_datetime = datetime.datetime.fromtimestamp(reset_time)
                now = datetime.datetime.now()
                wait_time = reset_datetime - now

                if wait_time.total_seconds() > 0:
                    minutes = int(wait_time.total_seconds() / 60)
                    print(
                        f"⏰ Лимит сбросится через: {minutes} минут "
                        f"(в {reset_datetime.strftime('%H:%M:%S')})"
                    )
                else:
                    print("⏰ Лимит должен скоро сброситься")
    else:
        print("⚠️  Информация о лимите не найдена в заголовках")

    if response.status_code == 200:
        print("✅ API работает нормально")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - возможно, лимит исчерпан или нет прав")
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - ключ невалиден")
    else:
        print(f"⚠️  Неожиданный статус: {response.status_code}")
        print(f"Ответ: {response.text[:200]}")

except Exception as e:
    print(f"❌ Ошибка: {e}")
