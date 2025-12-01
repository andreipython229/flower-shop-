#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import warnings
from io import StringIO


class FilteredOutput:
    def __init__(self, original):
        self.original = original
        self.buffer = StringIO()

    def write(self, s):
        # Фильтруем предупреждение о development server
        if isinstance(s, str):
            if "WARNING: This is a development server" in s:
                return
            if "Do not use it in a production setting" in s:
                return
            if "Use a production WSGI or ASGI server" in s:
                return
            if "For more information on production servers" in s:
                return
        self.original.write(s)

    def flush(self):
        self.original.flush()

    def __getattr__(self, name):
        return getattr(self.original, name)


# Подавление предупреждений об устаревших пакетах
warnings.filterwarnings("ignore", category=UserWarning, module="coreapi")
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

# Подавление предупреждения о development server
os.environ.setdefault("DJANGO_SUPPRESS_DEV_SERVER_WARNING", "1")

# Перехватываем вывод только для команды runserver
if len(sys.argv) > 1 and sys.argv[1] == "runserver":
    sys.stdout = FilteredOutput(sys.stdout)
    sys.stderr = FilteredOutput(sys.stderr)


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
