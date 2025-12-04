# Настройка авторизации и регистрации

## Backend

### 1. Установите зависимости

```powershell
pip install djangorestframework-simplejwt
```

### 2. Создайте миграции

```powershell
python manage.py makemigrations accounts
python manage.py migrate
```

### 3. Запустите сервер

```powershell
python manage.py runserver
```

## API Endpoints

- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `GET /api/auth/profile/` - Профиль пользователя (требует авторизации)
- `POST /api/auth/token/refresh/` - Обновление токена

## Примеры запросов

### Регистрация
```json
POST /api/auth/register/
{
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "password": "securepassword123",
  "password2": "securepassword123",
  "phone": "+79991234567"
}
```

### Вход
```json
POST /api/auth/login/
{
  "username": "testuser",
  "password": "securepassword123"
}
```

### Ответ (регистрация/вход)
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "profile": {
      "phone": "+79991234567",
      "created_at": "2025-01-01T12:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

## Frontend

Токены автоматически сохраняются в `localStorage`:
- `accessToken` - токен доступа (действителен 1 день)
- `refreshToken` - токен обновления (действителен 7 дней)
- `user` - данные пользователя (JSON)

Приватные роуты защищены компонентом `ProtectedRoute`.


