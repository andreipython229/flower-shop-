from django.core.management.base import OutputWrapper
from django.core.management.commands.runserver import Command as BaseCommand


class FilteredOutputWrapper(OutputWrapper):
    def __init__(self, out, style_func=None, ending=None):
        super().__init__(out, style_func, ending)
        self._original_write = out.write if hasattr(out, "write") else None

    def write(self, msg="", style_func=None, ending=None):
        # Фильтруем предупреждение о development server
        if isinstance(msg, str):
            if "WARNING: This is a development server" in msg:
                return
            if "Do not use it in a production setting" in msg:
                return
            if "Use a production WSGI or ASGI server" in msg:
                return
            if "For more information on production servers" in msg:
                return
        super().write(msg, style_func, ending)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Создаем фильтрованный вывод
        original_stdout = self.stdout
        original_stderr = self.stderr

        # Заменяем на фильтрованные обертки
        self.stdout = FilteredOutputWrapper(
            original_stdout._out, original_stdout.style_func
        )
        self.stderr = FilteredOutputWrapper(
            original_stderr._out, original_stderr.style_func
        )

        try:
            # Вызываем родительский handle
            super().handle(*args, **options)
        finally:
            # Восстанавливаем оригинальные выводы
            self.stdout = original_stdout
            self.stderr = original_stderr
