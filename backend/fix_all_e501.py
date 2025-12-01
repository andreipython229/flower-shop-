"""Автоматическое исправление всех E501 ошибок (длинные строки)"""

import re
from pathlib import Path


def split_long_line(line, max_length=88):
    """Разбивает длинную строку на несколько строк"""
    stripped = line.rstrip()
    if len(stripped) <= max_length:
        return line

    indent = len(line) - len(line.lstrip())

    # Если это комментарий, оставляем как есть (black не трогает)
    if stripped.startswith("#"):
        return line

    # Если это строка с f-string или обычной строкой
    # Пробуем разбить по операторам или запятым
    if 'f"' in line or "f'" in line or '"' in line or "'" in line:
        # Находим длинную строку в кавычках
        # Пробуем разбить по логическим операторам
        if " | " in line and line.count("|") == 1:
            parts = line.split(" | ", 1)
            if len(parts) == 2:
                return f"{parts[0]} |\n{' ' * (indent + 8)}{parts[1].lstrip()}"

        if " + " in line and line.count("+") == 1:
            parts = line.split(" + ", 1)
            if len(parts) == 2:
                return f"{parts[0]} +\n{' ' * (indent + 8)}{parts[1].lstrip()}"

    # Если это вызов функции с длинным аргументом
    if "(" in line and ")" in line and "," in line:
        # Пробуем разбить по запятым внутри скобок
        match = re.search(r"\(([^)]{90,})\)", line)
        if match:
            args = match.group(1)
            arg_parts = [a.strip() for a in args.split(",")]
            if len(arg_parts) > 1:
                new_args = (
                    ",\n"
                    + " " * (indent + 8)
                    + (",\n" + " " * (indent + 8)).join(arg_parts)
                )
                return re.sub(r"\([^)]{90,}\)", f"({new_args}\n{' ' * indent})", line)

    # Если это длинная f-string, пробуем разбить
    fstring_match = re.search(r'f"([^"]{90,})"', line)
    if fstring_match:
        content = fstring_match.group(1)
        # Разбиваем по пробелам или операторам
        if " - " in content:
            parts = content.split(" - ", 1)
            new_content = f"{parts[0]} -\n{' ' * (indent + 24)}{parts[1]}"
            return line.replace(f'f"{content}"', f'f"{new_content}"')

    return line


def process_file(file_path):
    """Обрабатывает один файл"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        changed = False
        for i, line in enumerate(lines):
            new_line = split_long_line(line)
            if new_line != line:
                changed = True
            new_lines.append(new_line)

        if changed:
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
        and f.name != "fix_all_e501.py"
    ]

    print(f"Обработка {len(python_files)} файлов...")
    fixed = 0

    for file_path in python_files:
        if process_file(file_path):
            fixed += 1

    print(f"\nГотово! Исправлено файлов: {fixed}")
    print("Запустите 'black .' для финального форматирования")
