from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "address",
            "comment",
            "items",
            "total",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]
