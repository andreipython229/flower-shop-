from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone", "email", "total", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "phone", "email"]
    list_editable = ["status"]
    readonly_fields = ["created_at"]
