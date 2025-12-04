"""Автоматическое исправление длинных строк в fix_*.py файлах"""

import os
import re

# Список файлов с проблемными строками
files_to_fix = [
    "fix_flower_images_from_folder.py",
    "fix_flower_images_unsplash.py",
    "fix_orange_roses_11.py",
    "fix_pink_carnations_25_final.py",
    "fix_pink_carnations_30_simple.py",
    "fix_pink_carnations_both.py",
    "fix_pink_eustoma_9.py",
    "fix_pink_gerberas_21.py",
    "fix_pink_gerberas_9.py",
    "fix_red_carnations_15.py",
    "fix_red_carnations_30.py",
    "fix_two_tone_roses.py",
    "fix_white_carnations_118.py",
    "fix_white_carnations_119.py",
    "fix_white_gerberas.py",
    "fix_white_lilies_7.py",
    "fix_white_lilies_74.py",
    "fix_white_lilies_75.py",
    "fix_white_lilies_9.py",
    "fix_white_peonies_5.py",
    "fix_white_peonies_7.py",
    "fix_white_peonies_9.py",
    "fix_white_roses_11.py",
    "fix_white_roses_15.py",
    "fix_white_roses_25.py",
    "fix_white_roses_35.py",
    "fix_white_roses_35_only.py",
    "fix_yellow_orchids_3.py",
    "fix_yellow_roses.py",
    "fix_yellow_roses_15.py",
]


def fix_long_line(line, max_length=88):
    """Исправляет длинную строку, разбивая её на несколько"""
    if len(line.rstrip()) <= max_length:
        return line

    # Если это docstring в начале файла
    if line.strip().startswith('"""') and len(line) > max_length:
        # Разбиваем docstring
        if line.strip().endswith('"""'):
            content = line.strip()[3:-3]
        else:
            content = line.strip()[3:]
        if len(content) > max_length - 7:  # Учитываем кавычки и отступ
            # Разбиваем на слова
            words = content.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= max_length - 7:
                    current_line += (" " if current_line else "") + word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            # Формируем многострочный docstring
            indent = len(line) - len(line.lstrip())
            result = " " * indent + '"""' + lines[0] + "\n"
            for line_part in lines[1:]:
                result += " " * indent + line_part + "\n"
            result += " " * indent + '"""\n'
            return result

    # Если это f-string или обычная строка в кавычках
    if 'f"' in line or "f'" in line or '"' in line or "'" in line:
        # Пытаемся найти строку в кавычках
        # Это сложно, лучше просто разбить по логическим местам
        if "logger." in line or "print(" in line:
            # Для логов разбиваем строку внутри кавычек
            match = re.search(r'(logger\.\w+\(|print\()\s*["\'](.*?)["\']', line)
            if match:
                prefix = line[: match.start()]
                func_call = match.group(1)
                string_content = match.group(2)
                suffix = line[match.end() :]
                if len(string_content) > 50:
                    # Разбиваем строку пополам
                    mid = len(string_content) // 2
                    # Ищем место для разбивки (пробел)
                    split_pos = string_content.rfind(" ", 0, mid)
                    if split_pos == -1:
                        split_pos = mid
                    part1 = string_content[:split_pos]
                    part2 = string_content[split_pos + 1 :]
                    quote = '"' if '"' in line else "'"
                    indent = len(line) - len(line.lstrip())
                    new_line = (
                        " " * indent
                        + prefix
                        + func_call
                        + quote
                        + part1
                        + quote
                        + "\n"
                        + " " * (indent + len(func_call))
                        + quote
                        + part2
                        + quote
                        + suffix
                    )
                    return new_line

    # Если ничего не помогло, просто разбиваем по пробелам
    if len(line.strip()) > max_length:
        words = line.split()
        if len(words) > 1:
            indent = len(line) - len(line.lstrip())
            lines = []
            current = " " * indent
            for word in words:
                if len(current + " " + word) <= max_length:
                    current += (" " if current.strip() else "") + word
                else:
                    if current.strip():
                        lines.append(current)
                    current = " " * indent + word
            if current.strip():
                lines.append(current)
            return "\n".join(lines) + "\n"

    return line


def fix_file(filepath):
    """Исправляет длинные строки в файле"""
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    changed = False
    for i, line in enumerate(lines):
        if len(line.rstrip()) > 88:
            fixed = fix_long_line(line)
            if fixed != line:
                new_lines.append(fixed)
                changed = True
                print(f"{filepath}:{i+1} - исправлена длинная строка")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    return False


if __name__ == "__main__":
    fixed_count = 0
    for filename in files_to_fix:
        if fix_file(filename):
            fixed_count += 1
    print(f"\n✅ Исправлено файлов: {fixed_count}")
