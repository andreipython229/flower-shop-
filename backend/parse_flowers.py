import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from flowers.parsers import FlowerParser

if __name__ == "__main__":
    parser = FlowerParser()
    flowers_data = parser.parse_flowers()
    parser.save_flowers(flowers_data)
    print("Парсинг цветов завершён!")
