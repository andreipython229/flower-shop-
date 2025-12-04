import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .utils import send_order_confirmation_email, send_telegram_notification

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    Создаёт Stripe Checkout Session и возвращает URL для оплаты
    """
    try:
        # Получаем данные заказа из запроса
        order_data = request.data

        # Создаём заказ в базе данных
        order = Order.objects.create(
            user=request.user,
            name=order_data.get("name"),
            phone=order_data.get("phone"),
            email=order_data.get("email"),
            address=order_data.get("address"),
            comment=order_data.get("comment", ""),
            items=order_data.get("items", []),
            total=order_data.get("total"),
            status="pending",
        )

        # Создаём line items для Stripe
        line_items = []
        for item in order.items:
            line_items.append(
                {
                    "price_data": {
                        "currency": "rub",
                        "product_data": {
                            "name": item.get("name", "Цветок"),
                            "description": item.get("description", ""),
                        },
                        "unit_amount": int(
                            float(item.get("price", 0)) * 100
                        ),  # Конвертируем в копейки
                    },
                    "quantity": item.get("quantity", 1),
                }
            )

        # Создаём Checkout Session в Stripe
        # Используем фронтенд URL для редиректа
        frontend_url = "http://localhost:3000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=(
                f"{frontend_url}/order-success?session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=f"{frontend_url}/order-cancel",
            metadata={
                "order_id": order.id,
                "user_id": request.user.id,
            },
            customer_email=order.email,
        )

        # Сохраняем payment_intent_id в заказе
        order.payment_intent_id = checkout_session.id
        order.save()

        # Отправляем уведомления
        send_order_confirmation_email(order)
        send_telegram_notification(order)

        return Response(
            {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "order_id": order.id,
            },
            status=status.HTTP_200_OK,
        )

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def stripe_webhook(request):
    """
    Webhook для обработки событий от Stripe
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Обрабатываем событие
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"].get("order_id")

        try:
            order = Order.objects.get(id=order_id)
            order.status = "completed"
            order.save()
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    elif event["type"] == "checkout.session.async_payment_failed":
        session = event["data"]["object"]
        order_id = session["metadata"].get("order_id")

        try:
            order = Order.objects.get(id=order_id)
            order.status = "cancelled"
            order.save()
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({"status": "success"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_payment_status(request, session_id):
    """
    Проверяет статус оплаты по session_id и обновляет статус заказа
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        order_id = session.metadata.get("order_id")

        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # Обновляем статус заказа в зависимости от статуса оплаты
            if session.payment_status == "paid" and order.status != "completed":
                order.status = "completed"
                order.save()
            elif session.payment_status == "unpaid" and order.status == "pending":
                # Оставляем pending, если оплата ещё не прошла
                pass

            return Response(
                {
                    "status": session.payment_status,
                    "order_status": order.status,
                    "order_id": order.id,
                },
                status=status.HTTP_200_OK,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
