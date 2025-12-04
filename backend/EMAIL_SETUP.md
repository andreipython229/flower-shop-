# Настройка Email уведомлений

## Настройка в .env файле

Добавьте следующие переменные в файл `.env` в корне проекта `backend/`:

```env
# Email настройки
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Telegram уведомления (опционально)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

## Настройка Gmail

1. Включите двухфакторную аутентификацию в вашем Google аккаунте
2. Создайте "Пароль приложения":
   - Перейдите в [Настройки аккаунта Google](https://myaccount.google.com/)
   - Безопасность → Двухэтапная аутентификация → Пароли приложений
   - Создайте новый пароль приложения для "Почта"
   - Используйте этот пароль в `EMAIL_HOST_PASSWORD`

## Настройка Telegram бота (опционально)

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Узнайте ваш Chat ID:
   - Напишите боту [@userinfobot](https://t.me/userinfobot)
   - Скопируйте ваш Chat ID
4. Добавьте токен и Chat ID в `.env`

## Тестирование

После настройки email будет автоматически отправляться при создании заказа.

Для тестирования без реального email сервера можно использовать консольный бэкенд:

```python
# В settings.py временно замените:
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

Тогда письма будут выводиться в консоль Django.


