from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .stripe_views import (
    check_payment_status,
    create_checkout_session,
    stripe_webhook,
)
from .views import OrderViewSet

router = DefaultRouter()
router.register(r"orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("checkout/", create_checkout_session, name="checkout"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
    path(
        "payment-status/<str:session_id>/", check_payment_status, name="payment_status"
    ),
]
