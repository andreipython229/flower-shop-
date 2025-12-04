from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .models import UserProfile

User = get_user_model()

# Отменяем стандартную регистрацию User, если она уже есть
if admin.site.is_registered(User):
    admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "username",
        "full_name",
        "phone_display",
        "orders_count",
        "is_staff",
        "is_active",
        "date_joined",
    ]
    list_filter = [
        "is_staff",
        "is_active",
        "date_joined",
        "is_superuser",
    ]
    search_fields = [
        "email",
        "username",
        "first_name",
        "last_name",
        "profile__phone",
    ]
    ordering = ["-date_joined"]
    readonly_fields = ["date_joined", "last_login"]

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    def full_name(self, obj):
        """Полное имя пользователя"""
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "-"

    full_name.short_description = "Имя"

    def phone_display(self, obj):
        """Отображение телефона из профиля"""
        try:
            phone = obj.profile.phone
            return phone if phone else "-"
        except UserProfile.DoesNotExist:
            return "-"

    phone_display.short_description = "Телефон"

    def orders_count(self, obj):
        """Количество заказов пользователя"""
        count = obj.orders.count()
        if count > 0:
            url = reverse("admin:orders_order_changelist")
            return format_html(
                '<a href="{}?user__id__exact={}">{} заказов</a>',
                url,
                obj.id,
                count,
            )
        return "0 заказов"

    orders_count.short_description = "Заказы"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user_link",
        "phone",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "phone",
    ]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]

    def user_link(self, obj):
        """Ссылка на пользователя"""
        url = reverse("admin:auth_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)

    user_link.short_description = "Пользователь"
