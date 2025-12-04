"""Скрипт для автоматического исправления длинных строк (E501) в fix_*.py файлах"""

import os
import re

# Список файлов для исправления
files_to_fix = [
    "fix_carnations_118_121.py",
    "fix_carnations_all.py",
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


def break_long_line(line, max_length=88):
    """Разбивает длинную строку на несколько строк"""
    if len(line.rstrip()) <= max_length:
        return line

    # Если это docstring в начале файла
    if line.strip().startswith('"""') and len(line) > max_length:
        # Пытаемся разбить docstring
        if line.strip().endswith('"""'):
            content = line.strip()[3:-3]
        else:
            content = line.strip()[3:]
        if len(content) > max_length - 7:  # Учитываем отступ и """
            # Разбиваем по запятым, точкам или дефисам
            parts = re.split(r"([,.-]\s+)", content)
            result = []
            current = ""
            for part in parts:
                if len(current + part) > max_length - 7 and current:
                    result.append(current)
                    current = part
                else:
                    current += part
            if current:
                result.append(current)
            if result:
                indent = len(line) - len(line.lstrip())
                first_line = " " * indent + '"""' + result[0]
                other_lines = [" " * (indent + 4) + part for part in result[1:]]
                if other_lines:
                    last_line = other_lines[-1] + '"""'
                    return (
                        first_line
                        + "\n"
                        + "\n".join(other_lines[:-1])
                        + "\n"
                        + last_line
                        + "\n"
                    )
                else:
                    return first_line + '"""'
                return last_line + "\n"

    # Если это f-string или обычная строка
    if 'f"' in line or "f'" in line:
        # Пытаемся разбить f-string
        indent = len(line) - len(line.lstrip())
        # Ищем места для разбиения (после запятых, точек, пробелов)
        if 'f"' in line:
            quote = '"'
        else:
            quote = "'"
        # Простое разбиение: находим место после 80 символов
        if len(line) > max_length:
            # Ищем место для разбиения (после операторов, запятых)
            break_pos = max_length - 10
            for i in range(break_pos, len(line) - 10, -1):
                if line[i] in [" ", ",", ".", ":", ";"]:
                    before = line[: i + 1].rstrip()
                    after = line[i + 1 :].lstrip()
                    if after.startswith(quote) and before.endswith(quote):
                        # Это конец строки
                        return line
                    # Разбиваем f-string
                    if 'f"' in before or "f'" in before:
                        # Добавляем f и кавычку к следующей строке если нужно
                        if not after.startswith("f"):
                            after = "f" + quote + after if quote in after else after
                        return before + "\n" + " " * (indent + 8) + after
                    break

    return line


def fix_file(filename):
    """Исправляет длинные строки в файле"""
    if not os.path.exists(filename):
        print(f"⚠ Файл {filename} не найден")
        return False

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    changed = False

    for i, line in enumerate(lines, 1):
        # Проверяем длину строки (без учета завершающего \n)
        if len(line.rstrip()) > 88:
            # Пытаемся разбить
            fixed = break_long_line(line)
            if fixed != line:
                new_lines.append(fixed)
                changed = True
                line_len = len(line.rstrip())
                fixed_len = len(fixed.rstrip()) if fixed else "N/A"
                print(f"  Строка {i}: разбита ({line_len} -> {fixed_len})")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if changed:
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ {filename}: исправлено")
        return True
    else:
        print(f"⏭ {filename}: без изменений")
        return False


if __name__ == "__main__":
    print("Исправление длинных строк (E501) в fix_*.py файлах...\n")
    fixed_count = 0
    for filename in files_to_fix:
        if fix_file(filename):
            fixed_count += 1
    print(f"\n✅ Исправлено файлов: {fixed_count}/{len(files_to_fix)}")
