"""Автоматическое исправление ошибок flake8: F541 и E722"""

import re
from pathlib import Path


def fix_f541(content):
    """Исправляет f-strings без плейсхолдеров (F541)"""
    # Паттерн: "..." где нет { }
    pattern = r'"([^"]*)"'

    def replace(match):
        text = match.group(1)
        # Если нет { } в строке, заменяем на обычную строку
        if "{" not in text and "}" not in text:
            return f'"{text}"'
        return match.group(0)

    # Заменяем "..." без плейсхолдеров
    content = re.sub(pattern, replace, content)

    # Также для '...'
    pattern = r"'([^']*)'"

    def replace_single(match):
        text = match.group(1)
        if "{" not in text and "}" not in text:
            return f"'{text}'"
        return match.group(0)

    content = re.sub(pattern, replace_single, content)
    return content


def fix_e722(content):
    """Исправляет bare except (E722): except: → except Exception:"""
    # Заменяем except: на except Exception:
    # Но только если это не часть except Exception as e:
    content = re.sub(r"except:\s*$", "except Exception:", content, flags=re.MULTILINE)
    return content


def process_file(file_path):
    """Обрабатывает один файл"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        content = fix_f541(content)
        content = fix_e722(content)

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
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
        if "migrations" not in str(f) and ".venv" not in str(f) and "venv" not in str(f)
    ]

    print(f"Обработка {len(python_files)} файлов...")
    fixed = 0

    for file_path in python_files:
        if process_file(file_path):
            fixed += 1

    print(f"\nГотово! Исправлено файлов: {fixed}")
