from rest_framework import serializers

from .models import Category, Favorite, Flower


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class FlowerSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
    )
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Flower
        fields = [
            "id",
            "name",
            "description",
            "price",
            "image",
            "image_url",
            "category",
            "category_id",
            "in_stock",
            "created_at",
        ]
        read_only_fields = ["image_url"]

    def get_image_url(self, obj):
        # Приоритет: image_url > image (файл)
        if obj.image_url:
            return obj.image_url
        if obj.image:
            # Если это файл, возвращаем полный URL с версионированием для обхода кэша
            request = self.context.get("request")
            base_url = obj.image.url
            if request:
                base_url = request.build_absolute_uri(obj.image.url)

            # Добавляем версию на основе времени модификации файла (обход кэша браузера)
            try:
                import os

                from django.conf import settings

                file_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
                if os.path.exists(file_path):
                    pass

                    # Используем время модификации файла как версию
                    mtime = os.path.getmtime(file_path)
                    version = int(mtime)
                    # Добавляем версию как query параметр
                    separator = "&" if "?" in base_url else "?"
                    return f"{base_url}{separator}v={version}"
            except Exception:
                pass

            return base_url
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    flower = FlowerSerializer(read_only=True)
    flower_id = serializers.PrimaryKeyRelatedField(
        queryset=Flower.objects.all(),
        source="flower",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Favorite
        fields = ["id", "flower", "flower_id", "created_at"]
        read_only_fields = ["id", "created_at"]
