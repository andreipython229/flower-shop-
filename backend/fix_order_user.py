import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from accounts.models import User
from orders.models import Order

# Находим заказ без пользователя
order = Order.objects.filter(user=None).first()
if order:
    print(f"Найден заказ ID {order.id}, email: {order.email}")

    # Находим пользователя по email
    user = User.objects.filter(email=order.email).first()
    if user:
        order.user = user
        order.save()
        print(f"✅ Заказ {order.id} привязан к пользователю {user.email}")
    else:
        print(f"❌ Пользователь с email {order.email} не найден")
else:
    print("Нет заказов без пользователя")
