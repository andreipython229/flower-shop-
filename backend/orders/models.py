from django.db import models
from django.db.models import JSONField


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает обработки"),
        ("processing", "В обработке"),
        ("completed", "Завершен"),
        ("cancelled", "Отменен"),
    ]

    name = models.CharField(max_length=200, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес доставки")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    items = JSONField(default=list, verbose_name="Товары")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итого")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} от {self.name}"
