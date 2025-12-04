#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки Telegram уведомлений
"""
import os
import sys
from pathlib import Path

import django

# Настройка Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import requests
from django.conf import settings


def test_telegram_connection():
    """Тестирует подключение к Telegram API"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ TELEGRAM УВЕДОМЛЕНИЙ")
    print("=" * 60)

    # Проверяем наличие токена
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not bot_token:
        print("❌ ОШИБКА: TELEGRAM_BOT_TOKEN не настроен в .env")
        print("\n📝 Как получить токен:")
        print("1. Открой @BotFather в Telegram")
        print("2. Отправь /newbot")
        print("3. Следуй инструкциям")
        print("4. Скопируй токен и добавь в .env: TELEGRAM_BOT_TOKEN=твой_токен")
        return False

    if not chat_id:
        print("❌ ОШИБКА: TELEGRAM_CHAT_ID не настроен в .env")
        print("\n📝 Как получить Chat ID:")
        print("1. Открой @userinfobot в Telegram")
        print("2. Отправь любое сообщение")
        print("3. Скопируй Chat ID и добавь в .env: TELEGRAM_CHAT_ID=твой_chat_id")
        return False

    print(f"✅ Токен бота: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"✅ Chat ID: {chat_id}")
    print()

    # Тестируем отправку сообщения
    print("📤 Отправка тестового сообщения...")

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        message = (
            "🎉 Тестовое уведомление от Flower Shop!\n\n"
            "Если ты видишь это сообщение, значит Telegram уведомления "
            "настроены правильно! ✅"
        )

        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        response = requests.post(url, data=data, timeout=10)

        result = response.json()

        if result.get("ok"):
            print("✅ УСПЕХ! Сообщение отправлено в Telegram!")
            print("📱 Проверь свой Telegram - должно прийти тестовое сообщение")
            print()
            print("=" * 60)
            print("🎊 ВСЁ РАБОТАЕТ! Telegram уведомления настроены!")
            print("=" * 60)
            return True
        else:
            error_desc = result.get("description", "Неизвестная ошибка")
            print(f"❌ ОШИБКА: {error_desc}")

            # Проверяем специфичные ошибки
            if "chat not found" in error_desc.lower():
                print()
                print("💡 ВАЖНО: Сначала напиши боту @Tunejdec_bot в Telegram!")
                print("   1. Открой https://t.me/Tunejdec_bot")
                print("   2. Нажми 'Start' или отправь /start")
                print("   3. Затем запусти тест снова")
            elif "unauthorized" in error_desc.lower():
                print()
                print("💡 Проблема с токеном бота. Проверь TELEGRAM_BOT_TOKEN в .env")

            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ ОШИБКА при отправке: {str(e)}")
        print()
        print("💡 Возможные причины:")
        print("1. Неверный токен бота")
        print("2. Неверный Chat ID")
        print("3. Бот заблокирован или удалён")
        print("4. Проблемы с интернет-соединением")
        return False
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {str(e)}")
        return False


def get_updates():
    """Получает последние обновления от бота (для отладки)"""
    bot_token = settings.TELEGRAM_BOT_TOKEN

    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не настроен")
        return

    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        result = response.json()

        if result.get("ok") and result.get("result"):
            updates = result["result"]
            if updates:
                print("\n📋 Последние обновления от бота:")
                for update in updates[-5:]:  # Показываем последние 5
                    if "message" in update:
                        msg = update["message"]
                        chat = msg.get("chat", {})
                        print(f"  - Chat ID: {chat.get('id')}, Тип: {chat.get('type')}")
            else:
                print("\n📋 Нет обновлений. Отправь боту сообщение и попробуй снова.")
        else:
            print(f"❌ Ошибка при получении обновлений: {result.get('description')}")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")


if __name__ == "__main__":
    print()

    # Основной тест
    success = test_telegram_connection()

    if not success:
        print()
        print("🔍 Попытка получить информацию о последних обновлениях...")
        get_updates()
        print()
        print("💡 Совет: Убедись, что:")
        print("  1. Токен бота правильный")
        print("  2. Chat ID правильный")
        print("  3. Ты отправил хотя бы одно сообщение боту (если это личный чат)")
        print("  4. Бот добавлен в группу (если отправляешь в группу)")
