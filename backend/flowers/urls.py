from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, FavoriteViewSet, FlowerViewSet

router = DefaultRouter()
router.register(r"flowers", FlowerViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("", include(router.urls)),
]
