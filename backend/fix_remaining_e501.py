"""Массовое исправление оставшихся E501 ошибок"""
import re
from pathlib import Path


def fix_long_line(line, max_length=88):
    """Исправляет длинную строку"""
    stripped = line.rstrip()
    if len(stripped) <= max_length:
        return line

    indent = len(line) - len(line.lstrip())

    # Если это комментарий, разбиваем его
    if stripped.startswith("#"):
        if len(stripped) > max_length:
            # Пробуем разбить по словам
            words = stripped[1:].split()
            if len(words) > 1:
                # Разбиваем на две части
                mid = len(words) // 2
                part1 = " ".join(words[:mid])
                part2 = " ".join(words[mid:])
                return f"{' ' * indent}# {part1}\n{' ' * indent}# {part2}\n"
        return line

    # Если это f-string или обычная строка с длинным текстом
    if 'f"' in line or "f'" in line:
        # Пробуем разбить f-string
        fstring_match = re.search(r'f"([^"]{90,})"', line)
        if fstring_match:
            content = fstring_match.group(1)
            # Разбиваем по логическим операторам
            if " -> " in content:
                parts = content.split(" -> ", 1)
                new_content = f"{parts[0]} ->\n{' ' * (indent + 12)}{parts[1]}"
                return line.replace(f'f"{content}"', f'f"{new_content}"')
            elif " - " in content:
                parts = content.split(" - ", 1)
                new_content = f"{parts[0]} -\n{' ' * (indent + 12)}{parts[1]}"
                return line.replace(f'f"{content}"', f'f"{new_content}"')

    # Если это обычная строка в кавычках
    string_match = re.search(r'"([^"]{90,})"', line)
    if string_match:
        content = string_match.group(1)
        # Разбиваем по логическим операторам
        if " -> " in content:
            parts = content.split(" -> ", 1)
            new_content = f"{parts[0]} ->\n{' ' * (indent + 12)}{parts[1]}"
            return line.replace(f'"{content}"', f'"{new_content}"')

    return line


def process_file(file_path):
    """Обрабатывает один файл"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        changed = False
        for line in lines:
            new_line = fix_long_line(line)
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
        and f.name != "fix_remaining_e501.py"
    ]

    print(f"Обработка {len(python_files)} файлов...")
    fixed = 0

    for file_path in python_files:
        if process_file(file_path):
            fixed += 1

    print(f"\nГотово! Исправлено файлов: {fixed}")
    print("Запустите 'black .' для финального форматирования")

