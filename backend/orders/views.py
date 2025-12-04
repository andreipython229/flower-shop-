from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderSerializer
from .utils import send_order_confirmation_email, send_telegram_notification


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()  # Базовый queryset для роутера
    serializer_class = OrderSerializer
    permission_classes = [
        IsAuthenticated
    ]  # Только авторизованные могут создавать заказы

    def get_queryset(self):
        """Возвращает только заказы текущего пользователя"""
        if self.request.user and self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    def perform_create(self, serializer):
        """
        При создании заказа автоматически привязываем к пользователю
        и отправляем уведомления
        """
        if self.request.user and self.request.user.is_authenticated:
            order = serializer.save(user=self.request.user)
        else:
            # Если пользователь не аутентифицирован, пытаемся найти по email
            email = serializer.validated_data.get("email")
            if email:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                try:
                    user = User.objects.get(email=email)
                    order = serializer.save(user=user)
                except User.DoesNotExist:
                    order = serializer.save()
            else:
                order = serializer.save()

        # Отправляем уведомления
        send_order_confirmation_email(order)
        send_telegram_notification(order)
