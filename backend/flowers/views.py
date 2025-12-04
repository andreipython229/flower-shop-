from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Favorite, Flower
from .serializers import CategorySerializer, FavoriteSerializer, FlowerSerializer


class FlowerViewSet(viewsets.ModelViewSet):
    queryset = Flower.objects.filter(in_stock=True)
    serializer_class = FlowerSerializer
    permission_classes = [AllowAny]  # Публичный доступ к каталогу

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        category_id = request.query_params.get("category_id")
        if category_id:
            flowers = Flower.objects.filter(category_id=category_id, in_stock=True)
        else:
            flowers = Flower.objects.filter(in_stock=True)
        serializer = self.get_serializer(flowers, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()  # Базовый queryset для роутера
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только избранное текущего пользователя"""
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании автоматически привязываем к пользователю"""
        flower_id = self.request.data.get("flower")
        if not flower_id:
            flower_id = self.request.data.get("flower_id")
        serializer.save(user=self.request.user, flower_id=flower_id)
