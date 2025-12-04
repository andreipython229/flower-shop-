from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order_info",
        "user_link",
        "customer_info",
        "total_display",
        "status",
        "status_badge",
        "payment_info",
        "created_at",
        "view_link",
    ]
    list_filter = [
        "status",
        "created_at",
        ("created_at", admin.DateFieldListFilter),
    ]
    search_fields = [
        "name",
        "phone",
        "email",
        "address",
        "user__email",
        "user__username",
    ]
    list_editable = ["status"]
    readonly_fields = [
        "created_at",
        "payment_intent_id",
        "order_items_display",
        "total",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "user",
                    "status",
                    "created_at",
                )
            },
        ),
        (
            "Данные клиента",
            {
                "fields": (
                    "name",
                    "phone",
                    "email",
                    "address",
                    "comment",
                )
            },
        ),
        (
            "Заказ",
            {
                "fields": (
                    "order_items_display",
                    "total",
                )
            },
        ),
        (
            "Оплата",
            {
                "fields": ("payment_intent_id",),
            },
        ),
    )

    def order_info(self, obj):
        """Отображение информации о заказе"""
        return format_html(
            "<strong>Заказ #{}</strong><br><small>{}</small>",
            obj.id,
            obj.created_at.strftime("%d.%m.%Y %H:%M") if obj.created_at else "",
        )

    order_info.short_description = "Заказ"

    def user_link(self, obj):
        """Ссылка на пользователя"""
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return format_html('<span style="color: #999;">Гость</span>')

    user_link.short_description = "Пользователь"

    def customer_info(self, obj):
        """Информация о клиенте"""
        return format_html(
            "<strong>{}</strong><br>{}<br><small>{}</small>",
            obj.name,
            obj.phone,
            obj.email,
        )

    customer_info.short_description = "Клиент"

    def total_display(self, obj):
        """Отображение суммы с форматированием"""
        return format_html('<strong style="color: #4caf50;">{} ₽</strong>', obj.total)

    total_display.short_description = "Сумма"

    def status_badge(self, obj):
        """Цветной бейдж статуса"""
        colors = {
            "pending": "#2196f3",  # Синий
            "processing": "#ff9800",  # Оранжевый
            "completed": "#4caf50",  # Зелёный
            "cancelled": "#f44336",  # Красный
        }
        status_text = dict(Order.STATUS_CHOICES).get(obj.status, obj.status)
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 10px; '
            'border-radius: 15px; font-weight: bold;">{}</span>',
            color,
            status_text,
        )

    status_badge.short_description = "Статус"

    def payment_info(self, obj):
        """Информация об оплате"""
        if obj.payment_intent_id:
            return format_html(
                '<span style="color: #4caf50;">✓ Оплачен</span><br>'
                '<small style="color: #999;">{}</small>',
                obj.payment_intent_id[:20] + "...",
            )
        return format_html('<span style="color: #999;">Не оплачен</span>')

    payment_info.short_description = "Оплата"

    def order_items_display(self, obj):
        """Отображение товаров в заказе"""
        if not obj.items:
            return "Нет товаров"
        items_html = "<ul>"
        for item in obj.items:
            items_html += format_html(
                "<li><strong>{}</strong> - {} шт. × {} ₽ = {} ₽</li>",
                item.get("name", "Товар"),
                item.get("quantity", 1),
                item.get("price", 0),
                float(item.get("price", 0)) * int(item.get("quantity", 1)),
            )
        items_html += "</ul>"
        return mark_safe(items_html)

    order_items_display.short_description = "Товары"

    def view_link(self, obj):
        """Ссылка на просмотр заказа"""
        url = reverse("admin:orders_order_change", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" '
            'style="padding: 5px 10px; background: #417690; '
            'color: white; text-decoration: none; border-radius: 3px;">'
            "Просмотр</a>",
            url,
        )

    view_link.short_description = "Действия"

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related("user")
