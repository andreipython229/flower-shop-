import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

import stripe
from django.conf import settings

from orders.models import Order

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Находим все заказы с payment_intent_id (оплаченные через Stripe)
orders_with_payment = Order.objects.exclude(payment_intent_id__isnull=True).exclude(
    payment_intent_id=""
)

print(f"Найдено заказов с payment_intent_id: {orders_with_payment.count()}")

for order in orders_with_payment:
    try:
        # Получаем информацию о сессии из Stripe
        session = stripe.checkout.Session.retrieve(order.payment_intent_id)

        if session.payment_status == "paid" and order.status != "completed":
            order.status = "completed"
            order.save()
            print(f"✅ Заказ {order.id} обновлён: статус изменён на 'completed'")
        elif session.payment_status == "unpaid" and order.status == "pending":
            print(f"⏳ Заказ {order.id}: оплата ещё не завершена")
        else:
            print(f"ℹ️ Заказ {order.id}: статус уже правильный ({order.status})")

    except stripe.error.StripeError as e:
        print(f"❌ Ошибка при проверке заказа {order.id}: {e}")

print("\nГотово!")
