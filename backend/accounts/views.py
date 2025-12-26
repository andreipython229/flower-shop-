import logging

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Авторизация пользователя"""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Необходимо указать username и password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"error": "Неверные учетные данные"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Создаём профиль, если его нет
    from .models import UserProfile
    try:
        # Проверяем, есть ли профиль
        user.profile
    except UserProfile.DoesNotExist:
        # Создаём профиль, если его нет
        try:
            UserProfile.objects.create(user=user)
        except Exception as e:
            logger.error(f"Ошибка при создании профиля: {e}", exc_info=True)
            # Продолжаем без профиля
    except Exception as e:
        logger.error(f"Ошибка при проверке профиля: {e}", exc_info=True)
        # Продолжаем без профиля

    # Генерируем JWT токены
    try:
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return Response(
            {
                "user": user_data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Ошибка при генерации токенов или сериализации: {e}", exc_info=True)
        return Response(
            {"error": "Внутренняя ошибка сервера"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Получить профиль текущего пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
