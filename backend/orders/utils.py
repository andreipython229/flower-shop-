"""
Утилиты для отправки уведомлений о заказах
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order):
    """
    Отправляет email-уведомление о принятии заказа
    """
    try:
        logger.info(
            f"📧 Начинаю отправку email для заказа #{order.id} на {order.email}"
        )
        logger.info(f"📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

        subject = f"Ваш заказ №{order.id} принят - Flower Shop"

        # Подготавливаем данные для шаблона (вычисляем total для каждого товара)
        items_with_total = []
        for item in order.items:
            item_copy = item.copy()
            item_copy["total"] = float(item.get("price", 0)) * int(
                item.get("quantity", 1)
            )
            items_with_total.append(item_copy)

        context = {
            "order": order,
            "items": items_with_total,
        }

        # Рендерим HTML шаблон
        html_message = render_to_string(
            "orders/emails/order_confirmation.html",
            context,
        )

        # Рендерим текстовую версию
        plain_message = render_to_string(
            "orders/emails/order_confirmation.txt",
            context,
        )

        # Отправляем email
        print(f"\n{'='*60}")
        print(f"📧 ОТПРАВКА EMAIL ДЛЯ ЗАКАЗА #{order.id}")
        print(f"📧 Получатель: {order.email}")
        print(f"📧 Тема: {subject}")
        print(f"{'='*60}")

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,  # Показываем ошибки для отладки
        )

        logger.info(
            f"✅ Email отправлен для заказа #{order.id} "
            f"на {order.email} (результат: {result})"
        )
        print(f"✅ Email успешно отправлен (результат: {result})")
        print(f"{'='*60}\n")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке email для заказа #{order.id}: {str(e)}")
        print(f"\n{'='*60}")
        print(f"❌ ОШИБКА ПРИ ОТПРАВКЕ EMAIL ДЛЯ ЗАКАЗА #{order.id}")
        print(f"Ошибка: {str(e)}")
        print(f"{'='*60}\n")
        import traceback

        traceback.print_exc()
        return False


def send_telegram_notification(order):
    """
    Отправляет уведомление в Telegram (опционально)
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.debug(
            "Telegram уведомления не настроены (отсутствуют токен или chat_id)"
        )
        return False

    try:
        import requests

        message = (
            f"🆕 Новый заказ №{order.id}\n\n"
            f"👤 Клиент: {order.name}\n"
            f"📞 Телефон: {order.phone}\n"
            f"📧 Email: {order.email}\n"
            f"📍 Адрес: {order.address}\n"
            f"💰 Сумма: {order.total} ₽\n"
            f"📦 Товаров: {len(order.items)}\n"
            f"📅 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}"
        )

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
        }

        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()

        logger.info(f"Telegram уведомление отправлено для заказа #{order.id}")
        return True

    except Exception as e:
        logger.error(
            f"Ошибка при отправке Telegram уведомления для заказа #{order.id}: {str(e)}"
        )
        return False
