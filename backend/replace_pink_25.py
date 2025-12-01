"""Скрипт для замены base64 для розовых гвоздик (25 шт)"""

import re

# Новый base64 от пользователя
new_base64 = "data:image/jpeg;base64,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"

# Читаем файл
with open("upload_carnations_manual.py", "r", encoding="utf-8") as f:
    content = f.read()

# Заменяем весь старый base64 на новый
# Ищем строку с 'Розовые гвоздики (25 шт)' и заменяем значение
pattern = r"('Розовые гвоздики \(25 шт\)':\s*')([^']+)(',\s*#.*)"
replacement = r"\1" + new_base64 + r"\3"

new_content = re.sub(pattern, replacement, content)

# Записываем обратно
with open("upload_carnations_manual.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ Base64 заменен для 'Розовые гвоздики (25 шт)'")
