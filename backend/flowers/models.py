from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Flower(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(
        upload_to="flowers/", blank=True, null=True, verbose_name="Изображение (файл)"
    )
    image_url = models.URLField(blank=True, null=True, verbose_name="Изображение (URL)")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
    )
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Цветок"
        verbose_name_plural = "Цветы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Избранные цветы пользователя"""

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    flower = models.ForeignKey(
        Flower,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Цветок",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = [["user", "flower"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.flower.name}"
