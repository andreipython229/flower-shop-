from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, FlowerViewSet

router = DefaultRouter()
router.register(r"flowers", FlowerViewSet)
router.register(r"categories", CategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
