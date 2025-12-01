"""
Проверка реальных изображений по URL из маппинга
"""

import requests

# Проверяем основные URL
test_urls = {
    "белые розы": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "красные розы": (
        "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "белые фрезии": (
        "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
    "желтые альстромерии": (
        "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
        "?auto=compress&cs=tinysrgb&w=600"
    ),
}

print("Проверка URL изображений:")
print("=" * 80)

for name, url in test_urls.items():
    try:
        response = requests.head(url, timeout=5)
        print(f"{name}: {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print()
    except Exception as e:
        print(f"{name}: Ошибка - {e}")
        print()
