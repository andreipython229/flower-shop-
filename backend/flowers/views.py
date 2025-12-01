from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Flower
from .serializers import CategorySerializer, FlowerSerializer


class FlowerViewSet(viewsets.ModelViewSet):
    queryset = Flower.objects.filter(in_stock=True)
    serializer_class = FlowerSerializer

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
