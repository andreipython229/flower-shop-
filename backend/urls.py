from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home(request):
    return JsonResponse(
        {
            "message": "Flower Shop API",
            "version": "1.0",
            "endpoints": {
                "admin": "/admin/",
                "api_flowers": "/api/flowers/",
                "api_orders": "/api/orders/",
            },
        }
    )


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("flowers.urls")),
    path("api/", include("orders.urls")),
    path("api/auth/", include("accounts.urls")),
]

# Раздача медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
