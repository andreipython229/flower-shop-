"""Автоматическое исправление длинных строк (E501)"""

import re
from pathlib import Path


def fix_long_line(line, max_length=88):
    """Разбивает длинную строку на несколько строк"""
    if len(line.rstrip()) <= max_length:
        return line

    # Если это комментарий, просто возвращаем как есть
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return line

    # Если это строка с URL, разбиваем её
    if "http" in line and '"' in line:
        # Находим URL в строке
        url_match = re.search(r'"(https?://[^"]+)"', line)
        if url_match:
            url = url_match.group(1)
            # Разбиваем URL на части
            if len(url) > 60:
                # Разбиваем URL по параметрам
                parts = url.split("?")
                if len(parts) > 1:
                    base = parts[0]
                    params = "?" + parts[1]
                    # Заменяем URL на разбитый вариант
                    new_url = f'"{base}"\n        "{params}"'
                    line = line.replace(f'"{url}"', new_url)
                    return line

    # Если это f-string или обычная строка, пробуем разбить
    if 'f"' in line or "f'" in line or '"' in line or "'" in line:
        # Находим строку в кавычках
        string_match = re.search(r'(f?"[^"]{90,}"|f?\'[^\']{90,}\')', line)
        if string_match:
            long_string = string_match.group(1)
            # Пробуем разбить по словам или операторам
            if " | " in long_string:
                parts = long_string.split(" | ", 1)
                new_string = f"{parts[0]} |\n        {parts[1]}"
                line = line.replace(long_string, new_string)
                return line
            elif " + " in long_string:
                parts = long_string.split(" + ", 1)
                new_string = f"{parts[0]} +\n        {parts[1]}"
                line = line.replace(long_string, new_string)
                return line

    # Если это вызов функции с длинным аргументом
    if "(" in line and ")" in line:
        # Пробуем разбить по запятым
        if "," in line and line.count("(") == line.count(")"):
            # Это может быть вызов функции
            # Находим аргументы после открывающей скобки
            match = re.search(r"\(([^)]{90,})\)", line)
            if match:
                args = match.group(1)
                # Разбиваем по запятым
                arg_parts = [a.strip() for a in args.split(",")]
                if len(arg_parts) > 1:
                    # Форматируем аргументы на новых строках
                    new_args = ",\n        ".join(arg_parts)
                    line = re.sub(
                        r"\([^)]{90,}\)", f"(\n        {new_args}\n    )", line
                    )
                    return line

    return line


def process_file(file_path):
    """Обрабатывает один файл"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            new_line = fix_long_line(line)
            new_lines.append(new_line)

        # Проверяем, изменился ли файл
        if new_lines != lines:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"✓ Исправлен: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Ошибка в {file_path}: {e}")
        return False


if __name__ == "__main__":
    backend_dir = Path(__file__).parent
    python_files = list(backend_dir.rglob("*.py"))

    # Исключаем миграции и виртуальное окружение
    python_files = [
        f
        for f in python_files
        if "migrations" not in str(f)
        and ".venv" not in str(f)
        and "venv" not in str(f)
        and f.name != "fix_long_lines.py"
    ]

    print(f"Обработка {len(python_files)} файлов...")
    fixed = 0

    for file_path in python_files:
        if process_file(file_path):
            fixed += 1

    print(f"\nГотово! Исправлено файлов: {fixed}")
