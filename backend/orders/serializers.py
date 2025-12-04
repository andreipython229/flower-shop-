from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "name",
            "phone",
            "email",
            "address",
            "comment",
            "items",
            "total",
            "status",
            "payment_intent_id",
            "created_at",
        ]
        read_only_fields = ["id", "user", "status", "payment_intent_id", "created_at"]
