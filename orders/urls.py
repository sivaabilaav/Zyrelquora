from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [

    # Checkout
    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    # Razorpay payment
    path(
        'payment-success/',
        views.payment_success,
        name='payment_success'
    ),

    path(
        'payment-failed/',
        views.payment_failed,
        name='payment_failed'
    ),

    # My Orders
    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),

    # Order Details
    path(
        'order-details/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),
   #cancellation
    path(
    'cancel-order/<int:order_id>/',
    views.cancel_order,
    name='cancel_order'
),

]