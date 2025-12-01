"""Исправляет длинные URL в списках"""

import re
import sys

if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    print("Использование: python fix_urls_in_list.py <файл>")
    sys.exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Паттерн для поиска длинных URL в списках
# Ищем строки вида: "https://...?auto=compress&cs=tinysrgb&w=600",
pattern = r'"https://([^"]+)"'


def replace_url(match):
    url = match.group(1)
    # Разбиваем URL на базовую часть и параметры
    if "?" in url:
        base, params = url.split("?", 1)
        return '(\n        "https://' + base + '"\n        "?' + params + '"\n    )'
    else:
        return f'(\n        "https://{url}"\n    )'


# Заменяем все длинные URL (только те, что длиннее 88 символов)
def process_line(line):
    if len(line.rstrip()) > 88 and '"https://' in line:
        # Проверяем, есть ли комментарий в конце
        if "#" in line:
            url_part, comment = line.rsplit("#", 1)
            url_match = re.search(pattern, url_part)
            if url_match:
                new_url = replace_url(url_match)
                return url_part.replace(url_match.group(0), new_url) + "#" + comment
        else:
            url_match = re.search(pattern, line)
            if url_match:
                return line.replace(url_match.group(0), replace_url(url_match))
    return line


# Обрабатываем файл построчно
lines = content.split("\n")
new_lines = []
for line in lines:
    new_lines.append(process_line(line))

new_content = "\n".join(new_lines)

if new_content != content:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✓ Исправлены все URL в {file_path}")
else:
    print(f"⚠ Изменений не требуется в {file_path}")
