from django.contrib import admin

from .models import Category, Flower


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "category", "in_stock", "created_at"]
    list_filter = ["category", "in_stock", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["price", "in_stock"]
