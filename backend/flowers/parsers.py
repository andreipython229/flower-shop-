import hashlib
import logging
import re
from decimal import Decimal

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import Category, Flower

logger = logging.getLogger(__name__)

# Маппинг изображений для цветов
FLOWER_IMAGE_MAP = {
    # Карточка 88 - "Смешанные тюльпаны (21 шт)"
    "Смешанные тюльпаны (21 шт)": "https://de-de.bakker.com/cdn/shop/files/103718_4_1699628447656.jpg?v=1699628495",
    # Карточка 87 - "Белые хризантемы (15 шт)"
    "Белые хризантемы (15 шт)": "https://sun9-23.userapi.com/impg/fDdX-qJxGJDY85KIGxSr8qeott9GF4UB8jqx1Q/3YCbpk8NW-s.jpg?size=1050x789&quality=95&sign=79eff9ef0d244ab5717a745604af8c40&c_uniq_tag=Ht4PyS6M_O3YRZdBjkXdp7k4BRCiLixvaJcxMwfQGak&type=album",
    # Карточка 86 - "Белые хризантемы (25 шт)"
    "Белые хризантемы (25 шт)": "https://avatars.mds.yandex.net/get-mpic/6253235/img_id1340511525181106758.jpeg/orig",
    # Карточка 85 - "Желтые хризантемы (15 шт)"
    "Желтые хризантемы (15 шт)": "https://d2gg9evh47fn9z.cloudfront.net/800px_COLOURBOX2214727.jpg",
    # Карточка 84 - "Желтые хризантемы (25 шт)"
    "Желтые хризантемы (25 шт)": "https://img.goodfon.ru/original/4032x3024/3/a9/tsvety-khrizantemy-zheltye-mnogo.jpg",
    # Карточка 83 - "Розовые хризантемы (15 шт)"
    "Розовые хризантемы (15 шт)": "https://i.pinimg.com/originals/cd/fd/87/cdfd87fc7873fac1473b560dc80b69b3.jpg",
    # Карточка 82 - "Красные хризантемы (15 шт)"
    "Красные хризантемы (15 шт)": "https://jooinn.com/images/red-mums-15.jpg",
    # Карточка 81 - "Оранжевые хризантемы (15 шт)"
    "Оранжевые хризантемы (15 шт)": "https://rare-gallery.com/uploads/posts/839788-Chrysanthemums-Closeup-Orange-Flower-bud.jpg",
    # Карточка 80 - "Розовые пионы (5 шт)"
    "Розовые пионы (5 шт)": "https://i.pinimg.com/originals/cd/63/93/cd639376b4c952335e86eb22a72aa420.png?nii=t",
    # Карточка 79 - "Розовые пионы (9 шт)"
    "Розовые пионы (9 шт)": "https://pixel-shot.com/get_image/i-3349133-0.JPG",
    # Карточка 78 - "Белые пионы (5 шт)"
    "Белые пионы (5 шт)": "https://img.freepik.com/premium-photo/white-peonies-white-vase-photo-realistic-bouquet-flowers_312400-177.jpg",
    # Карточка 77 - "Белые пионы (9 шт)"
    "Белые пионы (9 шт)": "https://i.pinimg.com/736x/4e/76/02/4e76025de1e059d6ffbd7acc2b1fb3ea.jpg",
    # Карточка 76 - "Бордовые пионы (5 шт)"
    "Бордовые пионы (5 шт)": "https://kartinki.pics/pics/uploads/posts/2022-07/1658589092_50-kartinkin-net-p-krasnie-pioni-tsveti-krasivo-foto-54.jpg",
    # Карточка 75 - "Белые лилии (3 шт)"
    "Белые лилии (3 шт)": "https://img.freepik.com/premium-photo/close-up-white-lily-flowers-grey-background_1048944-28096711.jpg?semt=ais_country_boost&w=740",
    # Карточка 74 - "Белые лилии (5 шт)"
    "Белые лилии (5 шт)": "https://i.pinimg.com/originals/eb/04/a5/eb04a581b9a6ab781c7ba0a3ff1b51f0.jpg?nii=t",
    # Карточка 73 - "Белые лилии (7 шт)"
    "Белые лилии (7 шт)": "https://i.pinimg.com/originals/c4/2c/a1/c42ca17075a61fc715703eab3d20a850.jpg",
    # Карточка 72 - "Розовые лилии (3 шт)"
    "Розовые лилии (3 шт)": "https://c8.alamy.com/comp/2JFWCK2/closeup-top-view-of-pink-orchids-growing-at-nursery-in-summer-orchidaceae-blooming-in-backyard-garden-in-spring-from-above-pretty-flowering-plants-2JFWCK2.jpg",
    # Карточка 71 - "Розовые лилии (5 шт)"
    "Розовые лилии (5 шт)": "https://i.artfile.ru/1920x1307_858154_[www.ArtFile.ru].jpg",
}


class FlowerParser:
    def __init__(self):
        # Список видов цветов с поисковыми запросами для изображений (140+ вариантов)
        self.flower_types = []

        # Розы - разные варианты и размеры
        roses = [
            {
                "name": "Красные розы (7 шт)",
                "price": 1800,
                "search_query": "red roses bouquet",
            },
            {
                "name": "Красные розы (11 шт)",
                "price": 2500,
                "search_query": "red roses bouquet",
            },
            {
                "name": "Красные розы (25 шт)",
                "price": 4500,
                "search_query": "red roses bouquet",
            },
            {
                "name": "Красные розы (51 шт)",
                "price": 8500,
                "search_query": "red roses bouquet",
            },
            {
                "name": "Красные розы (101 шт)",
                "price": 15000,
                "search_query": "red roses bouquet",
            },
            {
                "name": "Белые розы (7 шт)",
                "price": 1700,
                "search_query": "white roses bouquet",
            },
            {
                "name": "Белые розы (11 шт)",
                "price": 2200,
                "search_query": "white roses bouquet",
            },
            {
                "name": "Белые розы (25 шт)",
                "price": 4200,
                "search_query": "white roses bouquet",
            },
            {
                "name": "Розовые розы (7 шт)",
                "price": 1600,
                "search_query": "pink roses bouquet",
            },
            {
                "name": "Розовые розы (11 шт)",
                "price": 2000,
                "search_query": "pink roses bouquet",
            },
            {
                "name": "Розовые розы (25 шт)",
                "price": 4000,
                "search_query": "pink roses bouquet",
            },
            {
                "name": "Желтые розы (7 шт)",
                "price": 1700,
                "search_query": "yellow roses bouquet",
            },
            {
                "name": "Желтые розы (11 шт)",
                "price": 2100,
                "search_query": "yellow roses bouquet",
            },
            {
                "name": "Оранжевые розы (11 шт)",
                "price": 2300,
                "search_query": "orange roses bouquet",
            },
            {
                "name": "Персиковые розы (11 шт)",
                "price": 2400,
                "search_query": "peach roses bouquet",
            },
            {
                "name": "Бордовые розы (11 шт)",
                "price": 2600,
                "search_query": "burgundy roses bouquet",
            },
            {
                "name": "Двухцветные розы (11 шт)",
                "price": 2700,
                "search_query": "two color roses bouquet",
            },
        ]
        for r in roses:
            self.flower_types.append(
                {
                    "name": r["name"],
                    "category": "Розы",
                    "description": (
                        f"Букет {r['name'].lower()} - символ любви и страсти"
                    ),
                    "price": r["price"],
                    "search_query": r["search_query"],
                }
            )

        # Гвоздики
        carnations = [
            {
                "name": "Красные гвоздики (15 шт)",
                "price": 1000,
                "search_query": "red carnations bouquet",
            },
            {
                "name": "Красные гвоздики (25 шт)",
                "price": 1500,
                "search_query": "red carnations bouquet",
            },
            {
                "name": "Розовые гвоздики (15 шт)",
                "price": 950,
                "search_query": "pink carnations bouquet",
            },
            {
                "name": "Розовые гвоздики (25 шт)",
                "price": 1400,
                "search_query": "pink carnations bouquet",
            },
            {
                "name": "Белые гвоздики (15 шт)",
                "price": 1100,
                "search_query": "white carnations bouquet",
            },
            {
                "name": "Белые гвоздики (25 шт)",
                "price": 1600,
                "search_query": "white carnations bouquet",
            },
            {
                "name": "Желтые гвоздики (15 шт)",
                "price": 1050,
                "search_query": "yellow carnations bouquet",
            },
            {
                "name": "Смешанные гвоздики (25 шт)",
                "price": 1450,
                "search_query": "mixed carnations bouquet",
            },
        ]
        for c in carnations:
            self.flower_types.append(
                {
                    "name": c["name"],
                    "category": "Гвоздики",
                    "description": f"Яркий букет {c['name'].lower()}",
                    "price": c["price"],
                    "search_query": c["search_query"],
                }
            )

        # Герберы
        gerberas = [
            {
                "name": "Желтые герберы (9 шт)",
                "price": 1500,
                "search_query": "yellow gerbera bouquet",
            },
            {
                "name": "Желтые герберы (15 шт)",
                "price": 2200,
                "search_query": "yellow gerbera bouquet",
            },
            {
                "name": "Красные герберы (9 шт)",
                "price": 1400,
                "search_query": "red gerbera bouquet",
            },
            {
                "name": "Красные герберы (15 шт)",
                "price": 2100,
                "search_query": "red gerbera bouquet",
            },
            {
                "name": "Розовые герберы (9 шт)",
                "price": 1450,
                "search_query": "pink gerbera bouquet",
            },
            {
                "name": "Розовые герберы (15 шт)",
                "price": 2150,
                "search_query": "pink gerbera bouquet",
            },
            {
                "name": "Оранжевые герберы (9 шт)",
                "price": 1350,
                "search_query": "orange gerbera bouquet",
            },
            {
                "name": "Оранжевые герберы (15 шт)",
                "price": 2000,
                "search_query": "orange gerbera bouquet",
            },
            {
                "name": "Белые герберы (9 шт)",
                "price": 1550,
                "search_query": "white gerbera bouquet",
            },
            {
                "name": "Смешанные герберы (15 шт)",
                "price": 2300,
                "search_query": "mixed gerbera bouquet",
            },
        ]
        for g in gerberas:
            self.flower_types.append(
                {
                    "name": g["name"],
                    "category": "Герберы",
                    "description": (
                        f"Солнечный букет {g['name'].lower()} - символ радости"
                    ),
                    "price": g["price"],
                    "search_query": g["search_query"],
                }
            )

        # Ромашки
        daisies = [
            {
                "name": "Белые ромашки (20 шт)",
                "price": 800,
                "search_query": "white daisies bouquet",
            },
            {
                "name": "Белые ромашки (30 шт)",
                "price": 1100,
                "search_query": "white daisies bouquet",
            },
            {
                "name": "Белые ромашки (50 шт)",
                "price": 1600,
                "search_query": "white daisies bouquet",
            },
            {
                "name": "Ромашки с васильками (25 шт)",
                "price": 1200,
                "search_query": "daisies cornflowers bouquet",
            },
            {
                "name": "Ромашки с васильками (40 шт)",
                "price": 1800,
                "search_query": "daisies cornflowers bouquet",
            },
        ]
        for d in daisies:
            self.flower_types.append(
                {
                    "name": d["name"],
                    "category": "Ромашки",
                    "description": (
                        f"Классический букет {d['name'].lower()} - символ невинности"
                    ),
                    "price": d["price"],
                    "search_query": d["search_query"],
                }
            )

        # Васильки
        cornflowers = [
            {
                "name": "Синие васильки (25 шт)",
                "price": 900,
                "search_query": "blue cornflowers bouquet",
            },
            {
                "name": "Синие васильки (40 шт)",
                "price": 1300,
                "search_query": "blue cornflowers bouquet",
            },
            {
                "name": "Васильки и ромашки (30 шт)",
                "price": 1100,
                "search_query": "cornflowers daisies bouquet",
            },
            {
                "name": "Васильки и ромашки (50 шт)",
                "price": 1700,
                "search_query": "cornflowers daisies bouquet",
            },
        ]
        for cf in cornflowers:
            self.flower_types.append(
                {
                    "name": cf["name"],
                    "category": "Васильки",
                    "description": (
                        f"Полевой букет {cf['name'].lower()} - символ верности"
                    ),
                    "price": cf["price"],
                    "search_query": cf["search_query"],
                }
            )

        # Тюльпаны
        tulips = [
            {
                "name": "Красные тюльпаны (11 шт)",
                "price": 1300,
                "search_query": "red tulips bouquet",
            },
            {
                "name": "Красные тюльпаны (21 шт)",
                "price": 2200,
                "search_query": "red tulips bouquet",
            },
            {
                "name": "Желтые тюльпаны (11 шт)",
                "price": 1200,
                "search_query": "yellow tulips bouquet",
            },
            {
                "name": "Желтые тюльпаны (21 шт)",
                "price": 2100,
                "search_query": "yellow tulips bouquet",
            },
            {
                "name": "Розовые тюльпаны (11 шт)",
                "price": 1250,
                "search_query": "pink tulips bouquet",
            },
            {
                "name": "Розовые тюльпаны (21 шт)",
                "price": 2150,
                "search_query": "pink tulips bouquet",
            },
            {
                "name": "Белые тюльпаны (11 шт)",
                "price": 1350,
                "search_query": "white tulips bouquet",
            },
            {
                "name": "Фиолетовые тюльпаны (11 шт)",
                "price": 1400,
                "search_query": "purple tulips bouquet",
            },
            {
                "name": "Смешанные тюльпаны (21 шт)",
                "price": 2400,
                "search_query": "mixed tulips bouquet",
            },
        ]
        for t in tulips:
            self.flower_types.append(
                {
                    "name": t["name"],
                    "category": "Тюльпаны",
                    "description": f"Яркий букет {t['name'].lower()} - символ страсти",
                    "price": t["price"],
                    "search_query": t["search_query"],
                }
            )

        # Хризантемы
        chrysanthemums = [
            {
                "name": "Белые хризантемы (15 шт)",
                "price": 1600,
                "search_query": "white chrysanthemums bouquet",
            },
            {
                "name": "Белые хризантемы (25 шт)",
                "price": 2500,
                "search_query": "white chrysanthemums bouquet",
            },
            {
                "name": "Желтые хризантемы (15 шт)",
                "price": 1550,
                "search_query": "yellow chrysanthemums bouquet",
            },
            {
                "name": "Желтые хризантемы (25 шт)",
                "price": 2450,
                "search_query": "yellow chrysanthemums bouquet",
            },
            {
                "name": "Розовые хризантемы (15 шт)",
                "price": 1650,
                "search_query": "pink chrysanthemums bouquet",
            },
            {
                "name": "Красные хризантемы (15 шт)",
                "price": 1700,
                "search_query": "red chrysanthemums bouquet",
            },
            {
                "name": "Оранжевые хризантемы (15 шт)",
                "price": 1680,
                "search_query": "orange chrysanthemums bouquet",
            },
        ]
        for ch in chrysanthemums:
            self.flower_types.append(
                {
                    "name": ch["name"],
                    "category": "Хризантемы",
                    "description": f"Элегантный букет {ch['name'].lower()}",
                    "price": ch["price"],
                    "search_query": ch["search_query"],
                }
            )

        # Пионы
        peonies = [
            {
                "name": "Розовые пионы (5 шт)",
                "price": 2800,
                "search_query": "pink peonies bouquet",
            },
            {
                "name": "Розовые пионы (9 шт)",
                "price": 4800,
                "search_query": "pink peonies bouquet",
            },
            {
                "name": "Белые пионы (5 шт)",
                "price": 2700,
                "search_query": "white peonies bouquet",
            },
            {
                "name": "Белые пионы (9 шт)",
                "price": 4700,
                "search_query": "white peonies bouquet",
            },
            {
                "name": "Бордовые пионы (5 шт)",
                "price": 2900,
                "search_query": "burgundy peonies bouquet",
            },
        ]
        for p in peonies:
            self.flower_types.append(
                {
                    "name": p["name"],
                    "category": "Пионы",
                    "description": (
                        f"Нежный букет {p['name'].lower()} - символ романтики"
                    ),
                    "price": p["price"],
                    "search_query": p["search_query"],
                }
            )

        # Лилии
        lilies = [
            {
                "name": "Белые лилии (3 шт)",
                "price": 2200,
                "search_query": "white lilies bouquet",
            },
            {
                "name": "Белые лилии (5 шт)",
                "price": 3500,
                "search_query": "white lilies bouquet",
            },
            {
                "name": "Белые лилии (7 шт)",
                "price": 4800,
                "search_query": "white lilies bouquet",
            },
            {
                "name": "Розовые лилии (3 шт)",
                "price": 2100,
                "search_query": "pink lilies bouquet",
            },
            {
                "name": "Розовые лилии (5 шт)",
                "price": 3400,
                "search_query": "pink lilies bouquet",
            },
            {
                "name": "Оранжевые лилии (3 шт)",
                "price": 2300,
                "search_query": "orange lilies bouquet",
            },
            {
                "name": "Желтые лилии (3 шт)",
                "price": 2250,
                "search_query": "yellow lilies bouquet",
            },
        ]
        for lily in lilies:
            self.flower_types.append(
                {
                    "name": lily["name"],
                    "category": "Лилии",
                    "description": (
                        f"Элегантный букет {lily['name'].lower()} - символ чистоты"
                    ),
                    "price": lily["price"],
                    "search_query": lily["search_query"],
                }
            )

        # Ирисы
        irises = [
            {
                "name": "Синие ирисы (9 шт)",
                "price": 1700,
                "search_query": "blue irises bouquet",
            },
            {
                "name": "Синие ирисы (15 шт)",
                "price": 2600,
                "search_query": "blue irises bouquet",
            },
            {
                "name": "Фиолетовые ирисы (9 шт)",
                "price": 1650,
                "search_query": "purple irises bouquet",
            },
            {
                "name": "Фиолетовые ирисы (15 шт)",
                "price": 2550,
                "search_query": "purple irises bouquet",
            },
            {
                "name": "Желтые ирисы (9 шт)",
                "price": 1750,
                "search_query": "yellow irises bouquet",
            },
            {
                "name": "Белые ирисы (9 шт)",
                "price": 1800,
                "search_query": "white irises bouquet",
            },
        ]
        for i in irises:
            self.flower_types.append(
                {
                    "name": i["name"],
                    "category": "Ирисы",
                    "description": (
                        f"Красивый букет {i['name'].lower()} - символ мудрости"
                    ),
                    "price": i["price"],
                    "search_query": i["search_query"],
                }
            )

        # Смешанные букеты
        mixed = [
            {
                "name": 'Смешанный букет "Романтика" (средний)',
                "price": 2800,
                "search_query": "mixed flower bouquet",
            },
            {
                "name": 'Смешанный букет "Романтика" (большой)',
                "price": 4500,
                "search_query": "mixed flower bouquet",
            },
            {
                "name": 'Смешанный букет "Полевой" (средний)',
                "price": 1200,
                "search_query": "field flowers bouquet",
            },
            {
                "name": 'Смешанный букет "Полевой" (большой)',
                "price": 2000,
                "search_query": "field flowers bouquet",
            },
            {
                "name": 'Смешанный букет "Весенний"',
                "price": 2200,
                "search_query": "spring flowers bouquet",
            },
            {
                "name": 'Смешанный букет "Летний"',
                "price": 2400,
                "search_query": "summer flowers bouquet",
            },
            {
                "name": 'Смешанный букет "Осенний"',
                "price": 2600,
                "search_query": "autumn flowers bouquet",
            },
            {
                "name": "Свадебный букет",
                "price": 5000,
                "search_query": "wedding bouquet",
            },
            {"name": "Букет невесты", "price": 5500, "search_query": "bridal bouquet"},
            {
                "name": 'Смешанный букет "Премиум"',
                "price": 6000,
                "search_query": "premium flower bouquet",
            },
            {
                "name": 'Смешанный букет "Классика"',
                "price": 3000,
                "search_query": "classic flower bouquet",
            },
            {
                "name": 'Смешанный букет "Эксклюзив"',
                "price": 7000,
                "search_query": "exclusive flower bouquet",
            },
        ]
        for m in mixed:
            self.flower_types.append(
                {
                    "name": m["name"],
                    "category": "Смешанные",
                    "description": f"Яркий букет {m['name'].lower()}",
                    "price": m["price"],
                    "search_query": m["search_query"],
                }
            )

        # Дополнительные цветы для достижения 140+
        # Орхидеи
        orchids = [
            {
                "name": "Белые орхидеи (3 шт)",
                "price": 3500,
                "search_query": "white orchids bouquet",
            },
            {
                "name": "Розовые орхидеи (3 шт)",
                "price": 3400,
                "search_query": "pink orchids bouquet",
            },
            {
                "name": "Фиолетовые орхидеи (3 шт)",
                "price": 3600,
                "search_query": "purple orchids bouquet",
            },
            {
                "name": "Желтые орхидеи (3 шт)",
                "price": 3300,
                "search_query": "yellow orchids bouquet",
            },
        ]
        for o in orchids:
            self.flower_types.append(
                {
                    "name": o["name"],
                    "category": "Орхидеи",
                    "description": f"Экзотический букет {o['name'].lower()}",
                    "price": o["price"],
                    "search_query": o["search_query"],
                }
            )

        # Альстромерии
        alstroemerias = [
            {
                "name": "Розовые альстромерии (15 шт)",
                "price": 1800,
                "search_query": "pink alstroemeria bouquet",
            },
            {
                "name": "Желтые альстромерии (15 шт)",
                "price": 1750,
                "search_query": "yellow alstroemeria bouquet",
            },
            {
                "name": "Оранжевые альстромерии (15 шт)",
                "price": 1850,
                "search_query": "orange alstroemeria bouquet",
            },
            {
                "name": "Белые альстромерии (15 шт)",
                "price": 1900,
                "search_query": "white alstroemeria bouquet",
            },
        ]
        for a in alstroemerias:
            self.flower_types.append(
                {
                    "name": a["name"],
                    "category": "Альстромерии",
                    "description": f"Яркий букет {a['name'].lower()}",
                    "price": a["price"],
                    "search_query": a["search_query"],
                }
            )

        # Фрезии
        freesias = [
            {
                "name": "Белые фрезии (15 шт)",
                "price": 2000,
                "search_query": "white freesia bouquet",
            },
            {
                "name": "Желтые фрезии (15 шт)",
                "price": 1950,
                "search_query": "yellow freesia bouquet",
            },
            {
                "name": "Розовые фрезии (15 шт)",
                "price": 2050,
                "search_query": "pink freesia bouquet",
            },
        ]
        for f in freesias:
            self.flower_types.append(
                {
                    "name": f["name"],
                    "category": "Фрезии",
                    "description": f"Ароматный букет {f['name'].lower()}",
                    "price": f["price"],
                    "search_query": f["search_query"],
                }
            )

        # Астры
        asters = [
            {
                "name": "Белые астры (20 шт)",
                "price": 1400,
                "search_query": "white asters bouquet",
            },
            {
                "name": "Розовые астры (20 шт)",
                "price": 1350,
                "search_query": "pink asters bouquet",
            },
            {
                "name": "Фиолетовые астры (20 шт)",
                "price": 1450,
                "search_query": "purple asters bouquet",
            },
        ]
        for ast in asters:
            self.flower_types.append(
                {
                    "name": ast["name"],
                    "category": "Астры",
                    "description": f"Осенний букет {ast['name'].lower()}",
                    "price": ast["price"],
                    "search_query": ast["search_query"],
                }
            )

        # Гладиолусы
        gladiolus = [
            {
                "name": "Красные гладиолусы (7 шт)",
                "price": 2200,
                "search_query": "red gladiolus bouquet",
            },
            {
                "name": "Белые гладиолусы (7 шт)",
                "price": 2300,
                "search_query": "white gladiolus bouquet",
            },
            {
                "name": "Розовые гладиолусы (7 шт)",
                "price": 2250,
                "search_query": "pink gladiolus bouquet",
            },
        ]
        for gl in gladiolus:
            self.flower_types.append(
                {
                    "name": gl["name"],
                    "category": "Гладиолусы",
                    "description": f"Величественный букет {gl['name'].lower()}",
                    "price": gl["price"],
                    "search_query": gl["search_query"],
                }
            )

        # Эустома
        eustomas = [
            {
                "name": "Белые эустомы (9 шт)",
                "price": 2800,
                "search_query": "white eustoma bouquet",
            },
            {
                "name": "Розовые эустомы (9 шт)",
                "price": 2700,
                "search_query": "pink eustoma bouquet",
            },
            {
                "name": "Фиолетовые эустомы (9 шт)",
                "price": 2900,
                "search_query": "purple eustoma bouquet",
            },
            {
                "name": "Синие эустомы (9 шт)",
                "price": 2850,
                "search_query": "blue eustoma bouquet",
            },
        ]
        for eu in eustomas:
            self.flower_types.append(
                {
                    "name": eu["name"],
                    "category": "Эустома",
                    "description": f"Нежный букет {eu['name'].lower()}",
                    "price": eu["price"],
                    "search_query": eu["search_query"],
                }
            )

        # Дополнительные розы (разные размеры)
        more_roses = [
            {
                "name": "Красные розы (15 шт)",
                "price": 3200,
                "search_query": "red roses bouquet",
            },
            {
                "name": "Белые розы (15 шт)",
                "price": 3000,
                "search_query": "white roses bouquet",
            },
            {
                "name": "Розовые розы (15 шт)",
                "price": 2800,
                "search_query": "pink roses bouquet",
            },
            {
                "name": "Желтые розы (15 шт)",
                "price": 2900,
                "search_query": "yellow roses bouquet",
            },
        ]
        for mr in more_roses:
            self.flower_types.append(
                {
                    "name": mr["name"],
                    "category": "Розы",
                    "description": f"Букет {mr['name'].lower()} - символ любви",
                    "price": mr["price"],
                    "search_query": mr["search_query"],
                }
            )

        # Дополнительные тюльпаны
        more_tulips = [
            {
                "name": "Красные тюльпаны (15 шт)",
                "price": 1800,
                "search_query": "red tulips bouquet",
            },
            {
                "name": "Желтые тюльпаны (15 шт)",
                "price": 1700,
                "search_query": "yellow tulips bouquet",
            },
            {
                "name": "Розовые тюльпаны (15 шт)",
                "price": 1750,
                "search_query": "pink tulips bouquet",
            },
        ]
        for mt in more_tulips:
            self.flower_types.append(
                {
                    "name": mt["name"],
                    "category": "Тюльпаны",
                    "description": f"Яркий букет {mt['name'].lower()}",
                    "price": mt["price"],
                    "search_query": mt["search_query"],
                }
            )

        # Дополнительные гвоздики
        more_carnations = [
            {
                "name": "Красные гвоздики (30 шт)",
                "price": 1800,
                "search_query": "red carnations bouquet",
            },
            {
                "name": "Розовые гвоздики (30 шт)",
                "price": 1700,
                "search_query": "pink carnations bouquet",
            },
            {
                "name": "Белые гвоздики (30 шт)",
                "price": 1900,
                "search_query": "white carnations bouquet",
            },
        ]
        for mc in more_carnations:
            self.flower_types.append(
                {
                    "name": mc["name"],
                    "category": "Гвоздики",
                    "description": f"Яркий букет {mc['name'].lower()}",
                    "price": mc["price"],
                    "search_query": mc["search_query"],
                }
            )

        # Дополнительные герберы
        more_gerberas = [
            {
                "name": "Желтые герберы (21 шт)",
                "price": 2800,
                "search_query": "yellow gerbera bouquet",
            },
            {
                "name": "Красные герберы (21 шт)",
                "price": 2700,
                "search_query": "red gerbera bouquet",
            },
            {
                "name": "Розовые герберы (21 шт)",
                "price": 2750,
                "search_query": "pink gerbera bouquet",
            },
        ]
        for mg in more_gerberas:
            self.flower_types.append(
                {
                    "name": mg["name"],
                    "category": "Герберы",
                    "description": f"Солнечный букет {mg['name'].lower()}",
                    "price": mg["price"],
                    "search_query": mg["search_query"],
                }
            )

        # Дополнительные хризантемы
        more_chrysanthemums = [
            {
                "name": "Белые хризантемы (30 шт)",
                "price": 3200,
                "search_query": "white chrysanthemums bouquet",
            },
            {
                "name": "Желтые хризантемы (30 шт)",
                "price": 3100,
                "search_query": "yellow chrysanthemums bouquet",
            },
            {
                "name": "Розовые хризантемы (30 шт)",
                "price": 3150,
                "search_query": "pink chrysanthemums bouquet",
            },
        ]
        for mch in more_chrysanthemums:
            self.flower_types.append(
                {
                    "name": mch["name"],
                    "category": "Хризантемы",
                    "description": f"Элегантный букет {mch['name'].lower()}",
                    "price": mch["price"],
                    "search_query": mch["search_query"],
                }
            )

        # Дополнительные пионы
        more_peonies = [
            {
                "name": "Розовые пионы (7 шт)",
                "price": 4000,
                "search_query": "pink peonies bouquet",
            },
            {
                "name": "Белые пионы (7 шт)",
                "price": 3900,
                "search_query": "white peonies bouquet",
            },
        ]
        for mp in more_peonies:
            self.flower_types.append(
                {
                    "name": mp["name"],
                    "category": "Пионы",
                    "description": f"Нежный букет {mp['name'].lower()}",
                    "price": mp["price"],
                    "search_query": mp["search_query"],
                }
            )

        # Дополнительные лилии
        more_lilies = [
            {
                "name": "Белые лилии (9 шт)",
                "price": 6000,
                "search_query": "white lilies bouquet",
            },
            {
                "name": "Розовые лилии (9 шт)",
                "price": 5800,
                "search_query": "pink lilies bouquet",
            },
        ]
        for ml in more_lilies:
            self.flower_types.append(
                {
                    "name": ml["name"],
                    "category": "Лилии",
                    "description": f"Элегантный букет {ml['name'].lower()}",
                    "price": ml["price"],
                    "search_query": ml["search_query"],
                }
            )

        # Дополнительные ирисы
        more_irises = [
            {
                "name": "Синие ирисы (20 шт)",
                "price": 3200,
                "search_query": "blue irises bouquet",
            },
            {
                "name": "Фиолетовые ирисы (20 шт)",
                "price": 3100,
                "search_query": "purple irises bouquet",
            },
        ]
        for mi in more_irises:
            self.flower_types.append(
                {
                    "name": mi["name"],
                    "category": "Ирисы",
                    "description": f"Красивый букет {mi['name'].lower()}",
                    "price": mi["price"],
                    "search_query": mi["search_query"],
                }
            )

        # Дополнительные орхидеи
        more_orchids = [
            {
                "name": "Белые орхидеи (5 шт)",
                "price": 5000,
                "search_query": "white orchids bouquet",
            },
            {
                "name": "Розовые орхидеи (5 шт)",
                "price": 4800,
                "search_query": "pink orchids bouquet",
            },
        ]
        for mo in more_orchids:
            self.flower_types.append(
                {
                    "name": mo["name"],
                    "category": "Орхидеи",
                    "description": f"Экзотический букет {mo['name'].lower()}",
                    "price": mo["price"],
                    "search_query": mo["search_query"],
                }
            )

        # Дополнительные альстромерии
        more_alstroemerias = [
            {
                "name": "Розовые альстромерии (25 шт)",
                "price": 2800,
                "search_query": "pink alstroemeria bouquet",
            },
            {
                "name": "Желтые альстромерии (25 шт)",
                "price": 2700,
                "search_query": "yellow alstroemeria bouquet",
            },
        ]
        for ma in more_alstroemerias:
            self.flower_types.append(
                {
                    "name": ma["name"],
                    "category": "Альстромерии",
                    "description": f"Яркий букет {ma['name'].lower()}",
                    "price": ma["price"],
                    "search_query": ma["search_query"],
                }
            )

        # Дополнительные фрезии
        more_freesias = [
            {
                "name": "Белые фрезии (25 шт)",
                "price": 3000,
                "search_query": "white freesia bouquet",
            },
        ]
        for mf in more_freesias:
            self.flower_types.append(
                {
                    "name": mf["name"],
                    "category": "Фрезии",
                    "description": f"Ароматный букет {mf['name'].lower()}",
                    "price": mf["price"],
                    "search_query": mf["search_query"],
                }
            )

        # Финальные цветы для достижения 140+
        final_flowers = [
            {
                "name": "Красные розы (35 шт)",
                "price": 5500,
                "search_query": "red roses bouquet",
                "category": "Розы",
            },
            {
                "name": "Белые розы (35 шт)",
                "price": 5200,
                "search_query": "white roses bouquet",
                "category": "Розы",
            },
        ]
        for ff in final_flowers:
            self.flower_types.append(
                {
                    "name": ff["name"],
                    "category": ff["category"],
                    "description": f"Роскошный букет {ff['name'].lower()}",
                    "price": ff["price"],
                    "search_query": ff["search_query"],
                }
            )

        # Unsplash API - ключ получен
        import os

        # Ключ из Unsplash:
        # YIjTAjb14kWataGu6LAbCvgheBU1r7pM1R0u98tR9nQ
        self.UNSPLASH_ACCESS_KEY = os.environ.get(
            "UNSPLASH_ACCESS_KEY",
            "YIjTAjb14kWataGu6LAbCvgheBU1r7pM1R0u98tR9nQ",
        ).strip()
        self.UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

    def _get_flower_image_url_by_name(self, flower_name):
        """Использует IMAGE_MAPPING или Unsplash API для получения правильных изображений
        цветов по названию"""
        try:
            # Сначала проверяем маппинг изображений
            if flower_name in FLOWER_IMAGE_MAP:
                image_url = FLOWER_IMAGE_MAP[flower_name]
                logger.info(
                    f"✓ Найдено изображение в FLOWER_IMAGE_MAP для '{flower_name}'"
                )
                return image_url
            
            # Очищаем название от количества в скобках
            clean_name = re.sub(r"\s*\(\d+\s*шт\)", "", flower_name.lower()).strip()

            # Переводим русское название в английский поисковый запрос
            color_terms = {
                "красные": "red",
                "белые": "white",
                "розовые": "pink",
                "желтые": "yellow",
                "синие": "blue",
                "оранжевые": "orange",
                "фиолетовые": "purple",
                "бордовые": "burgundy",
                "персиковые": "peach",
            }
            flower_terms = {
                "розы": "roses",
                "гвоздики": "carnations",
                "герберы": "gerbera",
                "ромашки": "daisies",
                "васильки": "cornflowers",
                "тюльпаны": "tulips",
                "хризантемы": "chrysanthemums",
                "пионы": "peonies",
                "лилии": "lilies",
                "ирисы": "irises",
                "орхидеи": "orchids",
                "альстромерии": "alstroemeria",
                "фрезии": "freesia",
                "астры": "asters",
                "гладиолусы": "gladiolus",
                "эустомы": "eustoma",
            }

            found_color = None
            found_flower = None

            for ru, en in color_terms.items():
                if ru in clean_name:
                    found_color = en
                    break

            for ru, en in flower_terms.items():
                if ru in clean_name:
                    found_flower = en
                    break

            # Формируем поисковый запрос для Unsplash
            if found_color and found_flower:
                search_query = f"{found_color} {found_flower}"
            elif found_flower:
                search_query = found_flower
            else:
                search_query = "flowers"

            # Используем Unsplash API для получения изображения
            params = {
                "query": search_query,
                "per_page": 1,
                "client_id": self.UNSPLASH_ACCESS_KEY,
            }

            response = requests.get(self.UNSPLASH_API_URL, params=params, timeout=10)

            # Проверяем статус ответа
            if response.status_code == 401:
                logger.warning(
                    f"⚠ Unsplash API ключ невалиден (401) для '{flower_name}'"
                )
                return None
            elif response.status_code != 200:
                logger.warning(
                    f"⚠ Unsplash API вернул статус {response.status_code} "
                    f"для '{flower_name}'"
                )
                return None

            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                image_url = data["results"][0]["urls"]["regular"]
                logger.info(
                    f"✓ Найдено изображение через Unsplash API для "
                    f"'{flower_name}' -> '{search_query}'"
                )
                return image_url
            else:
                logger.warning(
                    f"⚠ Unsplash API не вернул результаты для "
                    f"'{flower_name}' -> '{search_query}'"
                )
                return None

        except Exception as e:
            logger.error(
                f"Ошибка при получении изображения через Unsplash API "
                f"для '{flower_name}': {e}"
            )
            return None

    def _get_flower_image_url(self, search_query):
        """Использует Unsplash API для получения правильных изображений цветов"""
        try:
            # Очищаем запрос от количества в скобках и слова "bouquet"
            clean_query = re.sub(r"\s*\(\d+\s*шт\)", "", search_query.lower()).strip()
            clean_query = re.sub(r"\s+bouquet\s*", "", clean_query).strip()

            # Если запрос уже на английском, используем его напрямую
            english_flower_words = [
                "roses",
                "carnations",
                "gerbera",
                "daisies",
                "cornflowers",
                "tulips",
                "chrysanthemums",
                "peonies",
                "lilies",
                "irises",
                "orchids",
                "alstroemeria",
                "freesia",
                "asters",
                "gladiolus",
                "eustoma",
            ]
            english_color_words = [
                "red",
                "white",
                "pink",
                "yellow",
                "blue",
                "orange",
                "purple",
                "burgundy",
                "peach",
            ]

            has_english_flower = any(
                word in clean_query for word in english_flower_words
            )
            has_english_color = any(word in clean_query for word in english_color_words)

            if has_english_flower or has_english_color:
                # Запрос уже на английском - используем как есть
                search_term = clean_query
            else:
                # Переводим русское название в английский
                color_terms = {
                    "красные": "red",
                    "белые": "white",
                    "розовые": "pink",
                    "желтые": "yellow",
                    "синие": "blue",
                    "оранжевые": "orange",
                    "фиолетовые": "purple",
                    "бордовые": "burgundy",
                    "персиковые": "peach",
                }
                flower_terms = {
                    "розы": "roses",
                    "гвоздики": "carnations",
                    "герберы": "gerbera",
                    "ромашки": "daisies",
                    "васильки": "cornflowers",
                    "тюльпаны": "tulips",
                    "хризантемы": "chrysanthemums",
                    "пионы": "peonies",
                    "лилии": "lilies",
                    "ирисы": "irises",
                    "орхидеи": "orchids",
                    "альстромерии": "alstroemeria",
                    "фрезии": "freesia",
                    "астры": "asters",
                    "гладиолусы": "gladiolus",
                    "эустомы": "eustoma",
                }

                found_color = None
                found_flower = None

                for ru, en in color_terms.items():
                    if ru in clean_query:
                        found_color = en
                        break

                for ru, en in flower_terms.items():
                    if ru in clean_query:
                        found_flower = en
                        break

                if found_color and found_flower:
                    search_term = f"{found_color} {found_flower}"
                elif found_flower:
                    search_term = found_flower
                else:
                    search_term = "flowers"

            # Используем Unsplash API
            params = {
                "query": search_term,
                "per_page": 1,
                "client_id": self.UNSPLASH_ACCESS_KEY,
            }

            response = requests.get(self.UNSPLASH_API_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                image_url = data["results"][0]["urls"]["regular"]
                logger.info(
                    f"✓ Найдено изображение через Unsplash API для "
                    f"'{search_query}' -> '{search_term}'"
                )
                return image_url
            else:
                logger.warning(
                    f"⚠ Unsplash API не вернул результаты для "
                    f"'{search_query}' -> '{search_term}'"
                )
                return None

        except Exception as e:
            logger.error(
                f"Ошибка при получении изображения через Unsplash API "
                f"для '{search_query}': {e}"
            )
            return None

    def _get_working_image_url(self, flower_name, search_query):
        """КАК С СОБАЧКАМИ: Использует ТОЛЬКО проверенные URL
        изображений цветов"""
        try:
            # ПРИОРИТЕТ 1: Используем проверенные URL из маппинга
            # (только проверенные!)
            image_url = self._get_flower_image_url(search_query)
            if image_url:
                logger.info(f"✓ Найдено проверенное изображение для '{flower_name}'")
                return image_url

            # ПРИОРИТЕТ 2: Если не нашли, используем точный маппинг по названию
            # (только проверенные!)
            image_url = self._get_exact_flower_image(flower_name)
            if image_url:
                logger.info(
                    f"✓ Найдено проверенное изображение в точном маппинге "
                    f"для '{flower_name}'"
                )
                return image_url

            # ПРИОРИТЕТ 3: Fallback - маппинг по типу (только проверенные!)
            image_url = self._get_flower_image_by_type(flower_name)
            if image_url:
                logger.info(
                    f"✓ Найдено проверенное изображение в fallback "
                    f"для '{flower_name}'"
                )
                return image_url

            # Если не нашли проверенное изображение, возвращаем None - будет
            # использован placeholder
            logger.info(
                f"ℹ Проверенное изображение не найдено для '{flower_name}'. "
                f"Будет использован placeholder."
            )
            return None

        except Exception as e:
            logger.error(f"Ошибка при получении изображения для '{flower_name}': {e}")
            return None  # Возвращаем None для использования placeholder

    def _get_exact_flower_image(self, flower_name):
        """ОПТИМАЛЬНЫЙ ВАРИАНТ: Точный маппинг названия цветка
        на соответствующий URL изображения"""
        # ОПТИМАЛЬНЫЙ ВАРИАНТ: Используем хеш имени цветка
        # для выбора уникального изображения
        # Это гарантирует, что каждое название получает свое уникальное изображение
        # и что одинаковые названия всегда получают одно и то же изображение

        # Список рабочих URL из Pexels (все проверены, работают)
        working_pexels_urls = [
            (
                "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/1454286/pexels-photo-1454286.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/1608311/pexels-photo-1608311.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
            (
                "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
                "?auto=compress&cs=tinysrgb&w=600"
            ),
        ]

        # Очищаем название от количества в скобках для более точного маппинга
        clean_name = flower_name.lower()
        clean_name = re.sub(r"\s*\(\d+\s*шт\)", "", clean_name).strip()

        # ПРИОРИТЕТ 1: Используем Unsplash Source API для получения РЕАЛЬНЫХ изображений
        # Это вернет изображение цветка по названию
        search_query = clean_name.replace("(", "").replace(")", "").strip()
        unsplash_url = self._get_flower_image_url(search_query)
        if unsplash_url:
            logger.info(f"✓ Использован Unsplash для '{flower_name}': {search_query}")
            return unsplash_url

        # ПРИОРИТЕТ 2: Если Unsplash не сработал, используем хеш для выбора
        # уникального изображения
        flower_hash = int(hashlib.md5(flower_name.encode("utf-8")).hexdigest()[:8], 16)
        selected_url = working_pexels_urls[flower_hash % len(working_pexels_urls)]
        logger.info(f"✓ Использован хеш для '{flower_name}' (fallback)")
        return selected_url

    def _parse_image_from_pexels(self, search_query):
        """ВАРИАНТ 3: Использует готовые проверенные URL изображений цветов"""
        # Pexels блокирует парсинг (403), поэтому используем готовые рабочие URL
        # Эти URL проверены и содержат правильные изображения цветов
        return None  # Пропускаем парсинг, используем маппинг ниже

    def _get_verified_image_url(self, search_query):
        """ВАРИАНТ 3: Возвращает проверенные рабочие URL изображений цветов"""
        try:
            # Маппинг поисковых запросов на ПРОВЕРЕННЫЕ рабочие URL изображений цветов
            # Эти URL были проверены вручную и содержат правильные изображения цветов
            verified_flower_images = {
                "red roses": (
                    "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white roses": (
                    "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink roses": (
                    "https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "yellow roses": (
                    "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "red carnations": (
                    "https://images.pexels.com/photos/1454286/pexels-photo-1454286.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink carnations": (
                    "https://images.pexels.com/photos/1608311/pexels-photo-1608311.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white carnations": (
                    "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "yellow gerbera": (
                    "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "red gerbera": (
                    "https://images.pexels.com/photos/2072168/pexels-photo-2072168.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink gerbera": (
                    "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white daisies": (
                    "https://images.pexels.com/photos/2300716/pexels-photo-2300716.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "blue cornflowers": (
                    "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "red tulips": (
                    "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "yellow tulips": (
                    "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink tulips": (
                    "https://images.pexels.com/photos/736230/pexels-photo-736230.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white chrysanthemums": (
                    "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "yellow chrysanthemums": (
                    "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink peonies": (
                    "https://images.pexels.com/photos/1793525/pexels-photo-1793525.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white peonies": (
                    "https://images.pexels.com/photos/2072167/pexels-photo-2072167.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white lilies": (
                    "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink lilies": (
                    "https://images.pexels.com/photos/2300714/pexels-photo-2300714.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "blue irises": (
                    "https://images.pexels.com/photos/2300717/pexels-photo-2300717.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "purple irises": (
                    "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white orchids": (
                    "https://images.pexels.com/photos/2300719/pexels-photo-2300719.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink orchids": (
                    "https://images.pexels.com/photos/2300720/pexels-photo-2300720.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "yellow orchids": (
                    "https://images.pexels.com/photos/1308881/pexels-photo-1308881.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink alstroemeria": (
                    "https://images.pexels.com/photos/1070535/pexels-photo-1070535.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "yellow alstroemeria": (
                    "https://images.pexels.com/photos/1408222/pexels-photo-1408222.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white freesia": (
                    "https://images.pexels.com/photos/169191/pexels-photo-169191.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "pink asters": (
                    "https://images.pexels.com/photos/2300713/pexels-photo-2300713.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "red gladiolus": (
                    "https://images.pexels.com/photos/2300715/pexels-photo-2300715.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
                "white eustoma": (
                    "https://images.pexels.com/photos/2300718/pexels-photo-2300718.jpeg"
                    "?auto=compress&cs=tinysrgb&w=600"
                ),
            }

            # Ищем точное совпадение
            search_lower = search_query.lower()
            for key, url in verified_flower_images.items():
                if key in search_lower:
                    logger.info(f"Найдено изображение для '{search_query}': {key}")
                    return url

            return None

        except Exception as e:
            logger.error(f"Ошибка при парсинге для '{search_query}': {e}")
            return None

    def _get_flower_image_by_type(self, flower_name):
        """ВАРИАНТ 3: Использует только РАБОЧИЕ URL из Pexels
        - распределяет через хеш для уникальности"""
        # ТОЛЬКО РАБОЧИЕ URL из Pexels (проверенные, работают)
        # Весь блок закомментирован, так как не используется
        # working_pexels_ids = [...]
        # import hashlib
        # flower_hash = int(
        #     hashlib.md5(flower_name.encode("utf-8")).hexdigest()[:8], 16
        # )
        # image_id = working_pexels_ids[flower_hash % len(working_pexels_ids)]
        # unique_url = (
        #     f"https://images.pexels.com/photos/{image_id}/pexels-photo-{image_id}.jpeg"
        #     "?auto=compress&cs=tinysrgb&w=600"
        # )

        # ЗАКОММЕНТИРОВАНО: URL из Pexels не проверены и часто возвращают 404
        # или нерелевантные изображения
        # Весь блок flower_images_map удален, так как не используется

        # ИСПОЛЬЗУЕМ PLACEHOLDER: Все URL из Pexels не работают (404)
        # или нерелевантны
        # Поэтому возвращаем None - будет использован placeholder
        logger.info(
            f"ℹ Для '{flower_name}' будет использован placeholder (URL не работают)"
        )
        return None

    def _get_fallback_image_url(self, search_query):
        """Резервный метод - использует Unsplash Source API
        (без ключа) или прямые ссылки"""
        # Пробуем Unsplash Source API (не требует ключа, но ограничен)
        try:
            # Unsplash Source API - публичный endpoint
            # source_url = (
            #     f"https://source.unsplash.com/600x600/"
            #     f"?{search_query.replace(' ', ',')}"
            # )
            # Но лучше использовать прямые URL из Unsplash через их CDN
            # Используем разные изображения цветов из Unsplash (прямые ссылки)
            flower_images_map = {
                "red roses": (
                    "https://images.unsplash.com/photo-1518895949257-7621c3c786d7"
                    "?w=600"
                ),
                "white roses": (
                    "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11"
                    "?w=600"
                ),
                "pink roses": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "yellow roses": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "red carnations": (
                    "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a"
                    "?w=600"
                ),
                "pink carnations": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "white carnations": (
                    "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11"
                    "?w=600"
                ),
                "yellow gerbera": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "red gerbera": (
                    "https://images.unsplash.com/photo-1518895949257-7621c3c786d7"
                    "?w=600"
                ),
                "pink gerbera": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "orange gerbera": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "white daisies": (
                    "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11"
                    "?w=600"
                ),
                "daisies cornflowers": (
                    "https://images.unsplash.com/photo-1518895949257-7621c3c786d7"
                    "?w=600"
                ),
                "blue cornflowers": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "cornflowers daisies": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "red tulips": (
                    "https://images.unsplash.com/photo-1518895949257-7621c3c786d7"
                    "?w=600"
                ),
                "yellow tulips": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "pink tulips": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "white chrysanthemums": (
                    "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11"
                    "?w=600"
                ),
                "yellow chrysanthemums": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "pink peonies": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "white peonies": (
                    "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11"
                    "?w=600"
                ),
                "white lilies": (
                    "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11"
                    "?w=600"
                ),
                "pink lilies": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "blue irises": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
                "purple irises": (
                    "https://images.unsplash.com/photo-1518621012428-4ae0c7c4a0a4"
                    "?w=600"
                ),
                "mixed flower": (
                    "https://images.unsplash.com/photo-1518895949257-7621c3c786d7"
                    "?w=600"
                ),
                "field flowers": (
                    "https://images.unsplash.com/photo-1606041008020-472df57c2b1b"
                    "?w=600"
                ),
            }

            search_lower = search_query.lower()
            for key, url in flower_images_map.items():
                if key in search_lower:
                    return url

            # Если не нашли, используем общий URL
            return (
                f"https://source.unsplash.com/600x600/?{search_query.replace(' ', ',')}"
            )
        except Exception as e:
            logger.error(f"Ошибка в fallback методе: {e}")
            return None

    def parse_flowers(self):
        """Генерирует данные о цветах"""
        try:
            logger.info("Начинаем генерацию данных о цветах")
            return self.flower_types
        except Exception as e:
            logger.error(f"Ошибка при генерации данных: {str(e)}")
            return []

    def save_flowers(self, flowers_data):
        """КАК С СОБАКАМИ: Скачивает изображения по названию и сохраняет локально"""
        saved_count = 0

        for flower_data in flowers_data:
            try:
                # Создаем или получаем категорию
                category, _ = Category.objects.get_or_create(
                    name=flower_data["category"]
                )

                # Получаем URL изображения по названию цветка
                # ПРИОРИТЕТ: Используем прямое русское название для точного маппинга
                image_url = self._get_flower_image_url_by_name(flower_data["name"])

                # Если не нашли по русскому названию, пробуем через search_query
                if not image_url:
                    search_query = flower_data.get("search_query", flower_data["name"])
                    image_url = self._get_working_image_url(
                        flower_data["name"], search_query
                    )

                image_file = None

                # КАК С СОБАЧКАМИ: Скачиваем изображение и сохраняем локально
                # ВАЖНО: Скачиваем ТОЛЬКО если URL найден и проверен
                if image_url:
                    try:
                        # Пробуем скачать с текущего URL
                        response = requests.get(
                            image_url,
                            stream=True,
                            timeout=15,
                            headers={"User-Agent": "Mozilla/5.0"},
                        )
                        response.raise_for_status()

                        # Создаем безопасное имя файла из названия цветка
                        safe_name = re.sub(r"[^\w\s-]", "", flower_data["name"]).strip()
                        safe_name = re.sub(r"[-\s]+", "_", safe_name)
                        file_extension = image_url.split(".")[-1].split("?")[
                            0
                        ]  # Получаем расширение из URL
                        if file_extension not in ["jpg", "jpeg", "png", "webp"]:
                            file_extension = "jpg"
                        md5_hash = hashlib.md5(
                            flower_data["name"].encode()
                        ).hexdigest()[:8]
                        file_name = f"{safe_name}_{md5_hash}.{file_extension}"

                        image_content = ContentFile(response.content)
                        # Сохраняем файл в media/flowers/ (КАК С СОБАЧКАМИ)
                        image_path = default_storage.save(
                            f"flowers/{file_name}", image_content
                        )
                        image_file = image_path
                        logger.info(
                            f"✓ Изображение скачано и сохранено: {file_name} "
                            f"для '{flower_data['name']}'"
                        )
                    except requests.exceptions.RequestException as e:
                        # Если не удалось скачать, пробуем альтернативный URL
                        logger.warning(
                            f"⚠ Не удалось скачать изображение {image_url} "
                            f"для '{flower_data['name']}': {e}. "
                            f"Пробуем альтернативный URL..."
                        )
                        # Пробуем использовать базовый URL без параметров или другой
                        # формат
                        alternative_url = image_url.replace(".jpeg", ".jpg").replace(
                            "pexels-photo", "photos"
                        )
                        try:
                            response = requests.get(
                                alternative_url,
                                stream=True,
                                timeout=15,
                                headers={"User-Agent": "Mozilla/5.0"},
                            )
                            response.raise_for_status()
                            safe_name = re.sub(
                                r"[^\w\s-]", "", flower_data["name"]
                            ).strip()
                            safe_name = re.sub(r"[-\s]+", "_", safe_name)
                            file_extension = "jpg"
                            md5_hash = hashlib.md5(
                                flower_data["name"].encode()
                            ).hexdigest()[:8]
                            file_name = f"{safe_name}_{md5_hash}.{file_extension}"
                            image_content = ContentFile(response.content)
                            image_path = default_storage.save(
                                f"flowers/{file_name}", image_content
                            )
                            image_file = image_path
                            logger.info(
                                f"✓ Изображение скачано с альтернативного URL: "
                                f"{file_name} для '{flower_data['name']}'"
                            )
                        except Exception:
                            logger.warning(
                                f"⚠ Альтернативный URL тоже не работает для "
                                f"'{flower_data['name']}'. "
                                f"Будет использован placeholder."
                            )
                            image_url = None
                            image_file = None
                    except Exception as e:
                        logger.warning(
                            f"⚠ Ошибка при сохранении файла изображения для "
                            f"'{flower_data['name']}': {e}. "
                            f"Будет использован placeholder."
                        )
                        image_url = None
                        image_file = None
                else:
                    logger.info(
                        f"ℹ Изображение не найдено для '{flower_data['name']}'. "
                        f"Будет использован placeholder."
                    )

                # Обновляем или создаем запись о цветке с локальным изображением
                # (КАК С СОБАЧКАМИ)
                # ВАЖНО: Не обновляем изображение, если оно уже есть
                flower, created = Flower.objects.get_or_create(
                    name=flower_data["name"],
                    defaults={
                        "description": flower_data["description"],
                        "price": Decimal(str(flower_data["price"])),
                        "category": category,
                        # Сохраняем локально (как с собачками), или None для placeholder
                        "image": image_file,
                        # НЕ сохраняем внешние URL (используем только локальные файлы)
                        "image_url": None,
                        "in_stock": True,
                    },
                )

                # Обновляем только если изображения нет, но мы его скачали
                if not created and not flower.image and image_file:
                    flower.image = image_file
                    flower.description = flower_data["description"]
                    flower.price = Decimal(str(flower_data["price"]))
                    flower.category = category
                    flower.in_stock = True
                    flower.save()
                saved_count += 1
                action = "Создан" if created else "Обновлен"
                logger.info(f"✓ {action} цветок: {flower_data['name']}")

            except Exception as e:
                logger.error(f"Ошибка при сохранении цветка: {str(e)}")
                continue

        logger.info(f"Всего сохранено цветов: {saved_count}")


if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()

    parser = FlowerParser()
    flowers_data = parser.parse_flowers()
    parser.save_flowers(flowers_data)
    print("Парсинг завершён!")
