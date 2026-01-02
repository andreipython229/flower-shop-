from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


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
    # Логируем входящие данные для отладки
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Login request data: {request.data}")
    logger.info(f"Request content type: {request.content_type}")
    
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        logger.warning(f"Missing credentials: username={username is not None}, password={password is not None}")
        return Response(
            {"error": "Необходимо указать username и password", "received_data": list(request.data.keys())},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"error": "Неверные учетные данные"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

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
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Получить профиль текущего пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
