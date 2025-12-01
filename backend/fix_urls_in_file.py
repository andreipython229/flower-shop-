"""Исправляет длинные URL в fix_flower_images.py"""

import re
import sys

if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    file_path = "fix_flower_images.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Паттерн для поиска длинных URL строк
# Ищем строки вида: "ключ": "https://...?auto=compress&cs=tinysrgb&w=600",
pattern = r'("[\w\s]+"):\s*"https://([^"]+)"'


def replace_url(match):
    key = match.group(1)
    url = match.group(2)

    # Разбиваем URL на базовую часть и параметры
    if "?" in url:
        base, params = url.split("?", 1)
        return f'{key}: (\n        "https://{base}"\n        "?{params}"\n    ),'
    else:
        return f'{key}: (\n        "https://{url}"\n    ),'


# Заменяем все длинные URL
new_content = re.sub(pattern, replace_url, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"✓ Исправлены все URL в {file_path}")
