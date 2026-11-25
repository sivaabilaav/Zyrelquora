
import logging
import razorpay
import re

from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .models import Order, OrderItem


logger = logging.getLogger(__name__)


# ==========================================
# RAZORPAY CLIENT - FUTURE USE
# ==========================================

def get_razorpay_client():

    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    if (
        not key_id
        or not key_secret
        or key_id == 'your_test_key_id'
        or key_secret == 'your_test_key_secret'
    ):
        raise ValueError(
            "Razorpay test credentials are not configured."
        )

    return razorpay.Client(
        auth=(key_id, key_secret)
    )


# ==========================================
# CREATE ORDER FROM CART
# ==========================================

def create_order_from_cart(request, details, payment_method):

    cart = request.session.get('cart', {})
    product_ids = list(cart.keys())

    with transaction.atomic():

        locked_products = Product.objects.select_for_update().filter(
            id__in=product_ids
        )

        product_map = {
            str(product.id): product
            for product in locked_products
        }

        order_products = []
        order_total = Decimal('0.00')

        for product_id, cart_item in cart.items():

            product = product_map.get(str(product_id))

            if product is None or not product.is_available:
                raise ValueError(
                    "A product in your cart is unavailable."
                )

            try:
                quantity = int(cart_item.get('quantity', 1))

            except (ValueError, TypeError, AttributeError):
                raise ValueError("Invalid product quantity.")

            if quantity < 1 or quantity > product.stock:
                raise ValueError(
                    f"Insufficient stock for {product.name}."
                )

            order_total += product.price * quantity

            order_products.append({
                'product': product,
                'quantity': quantity,
                'price': product.price,
            })

        order = Order.objects.create(
            user=request.user,
            full_name=details['full_name'],
            email=details['email'],
            phone=details['phone'],
            address=details['address'],
            city=details['city'],
            state=details['state'],
            pincode=details['pincode'],
            total_amount=order_total,
            payment_method=payment_method,
            payment_status='Pending',
        )

        for item in order_products:

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
            )

            if payment_method == 'Cash on Delivery':

                product = item['product']
                product.stock -= item['quantity']

                product.save(
                    update_fields=['stock']
                )

    return order


# ==========================================
# CHECKOUT
# ==========================================

@login_required
def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    product_ids = [
        product_id for product_id in cart.keys()
        if str(product_id).isdigit()
    ]

    if len(product_ids) != len(cart):
        messages.error(request, "Invalid cart items.")
        return redirect('cart')

    products = Product.objects.filter(id__in=product_ids)

    product_map = {
        str(product.id): product
        for product in products
    }

    checkout_items = []
    total_price = Decimal('0.00')

    for product_id, cart_item in cart.items():

        product = product_map.get(str(product_id))

        if product is None or not product.is_available:
            messages.error(
                request,
                "A product in your cart is no longer available."
            )
            return redirect('cart')

        try:
            quantity = int(cart_item.get('quantity', 1))

        except (ValueError, TypeError, AttributeError):
            messages.error(
                request,
                "Invalid product quantity."
            )
            return redirect('cart')

        if quantity < 1 or quantity > product.stock:
            messages.error(
                request,
                f"Please check available stock for {product.name}."
            )
            return redirect('cart')

        subtotal = product.price * quantity

        checkout_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

        total_price += subtotal

    # --------------------------------------
    # HANDLE CHECKOUT POST
    # --------------------------------------

    if request.method == 'POST':

        details = {
            'full_name': request.POST.get('full_name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'address': request.POST.get('address', '').strip(),
            'city': request.POST.get('city', '').strip(),
            'state': request.POST.get('state', '').strip(),
            'pincode': request.POST.get('pincode', '').strip(),
        }

        payment_method = request.POST.get('payment_method', '')

        # REQUIRED FIELD VALIDATION

        if not all(details.values()):
            messages.error(
                request,
                "Please complete all delivery details."
            )
            return redirect('orders:checkout')

        # FULL NAME VALIDATION

        if not re.fullmatch(
            r'[A-Za-z ]+',
            details['full_name']
        ):
            messages.error(
                request,
                "Full name must contain letters and spaces only."
            )
            return redirect('orders:checkout')

        # EMAIL VALIDATION

        try:
            validate_email(details['email'])

        except ValidationError:
            messages.error(
                request,
                "Please enter a valid email address."
            )
            return redirect('orders:checkout')

        # PHONE VALIDATION

        if not re.fullmatch(
            r'[0-9]{10}',
            details['phone']
        ):
            messages.error(
                request,
                "Phone number must contain exactly 10 digits."
            )
            return redirect('orders:checkout')

        # ADDRESS VALIDATION

        if len(details['address']) < 10:
            messages.error(
                request,
                "Please enter a complete delivery address."
            )
            return redirect('orders:checkout')

        # CITY VALIDATION

        if not re.fullmatch(
            r'[A-Za-z ]+',
            details['city']
        ):
            messages.error(
                request,
                "City must contain letters and spaces only."
            )
            return redirect('orders:checkout')

        # STATE VALIDATION

        if not re.fullmatch(
            r'[A-Za-z ]+',
            details['state']
        ):
            messages.error(
                request,
                "State must contain letters and spaces only."
            )
            return redirect('orders:checkout')

        # PIN CODE VALIDATION

        if not re.fullmatch(
            r'[0-9]{6}',
            details['pincode']
        ):
            messages.error(
                request,
                "PIN Code must contain exactly 6 digits."
            )
            return redirect('orders:checkout')

        # PAYMENT METHOD VALIDATION

        if payment_method not in [
            'Cash on Delivery',
            'Online Payment'
        ]:
            messages.error(
                request,
                "Please select a valid payment method."
            )
            return redirect('orders:checkout')

        # ONLINE PAYMENT TEMPORARILY DISABLED

        if payment_method == 'Online Payment':
            messages.warning(
                request,
                "Online payment is currently unavailable. "
                "Please choose Cash on Delivery."
            )
            return redirect('orders:checkout')

        # CREATE DATABASE ORDER

        try:
            order = create_order_from_cart(
                request,
                details,
                payment_method
            )

        except ValueError as error:
            messages.error(request, str(error))
            return redirect('cart')

        # CASH ON DELIVERY

        if payment_method == 'Cash on Delivery':

            request.session['cart'] = {}
            request.session.modified = True

            return render(
                request,
                'order_confirmation.html',
                {'order': order}
            )

    # DISPLAY CHECKOUT PAGE

    return render(
        request,
        'checkout.html',
        {
            'checkout_items': checkout_items,
            'total_price': total_price,
        }
    )


# ==========================================
# RAZORPAY PAYMENT SUCCESS - FUTURE USE
# ==========================================

@login_required
@require_POST
def payment_success(request):

    payment_id = request.POST.get(
        'razorpay_payment_id', ''
    )

    razorpay_order_id = request.POST.get(
        'razorpay_order_id', ''
    )

    signature = request.POST.get(
        'razorpay_signature', ''
    )

    if not all([
        payment_id,
        razorpay_order_id,
        signature
    ]):

        messages.error(
            request,
            "Incomplete payment response."
        )

        return redirect('orders:checkout')

    order = get_object_or_404(
        Order,
        user=request.user,
        razorpay_order_id=razorpay_order_id,
        payment_method='Online Payment',
    )

    if order.payment_status == 'Paid':

        return render(
            request,
            'order_confirmation.html',
            {'order': order}
        )

    if order.payment_status != 'Pending':

        messages.error(
            request,
            "This payment is no longer pending."
        )

        return redirect('orders:checkout')

    # VERIFY RAZORPAY PAYMENT

    try:

        client = get_razorpay_client()

        client.utility.verify_payment_signature({

            'razorpay_order_id':
                order.razorpay_order_id,

            'razorpay_payment_id':
                payment_id,

            'razorpay_signature':
                signature,

        })

        payment = client.payment.fetch(payment_id)

        expected_amount = int(
            order.total_amount * 100
        )

        if (
            payment.get('order_id') != order.razorpay_order_id
            or payment.get('amount') != expected_amount
            or payment.get('status') != 'captured'
        ):

            messages.error(
                request,
                "Payment could not be confirmed as captured."
            )

            return redirect('orders:checkout')

    except Exception:

        logger.exception(
            "Razorpay payment verification failed. "
            "Order ID: %s",
            order.id
        )

        messages.error(
            request,
            "Payment verification failed. "
            "Your order has not been confirmed."
        )

        return redirect('orders:checkout')

    # UPDATE ORDER AND REDUCE STOCK

    try:

        with transaction.atomic():

            locked_order = Order.objects.select_for_update().get(
                id=order.id
            )

            if locked_order.payment_status == 'Paid':

                return render(
                    request,
                    'order_confirmation.html',
                    {'order': locked_order}
                )

            if locked_order.payment_status != 'Pending':

                messages.error(
                    request,
                    "This payment is no longer pending."
                )

                return redirect('orders:checkout')

            order_items = list(
                locked_order.items.select_related('product')
            )

            product_ids = [
                item.product_id
                for item in order_items
            ]

            locked_products = Product.objects.select_for_update().filter(
                id__in=product_ids
            )

            product_map = {
                product.id: product
                for product in locked_products
            }

            for item in order_items:

                product = product_map.get(item.product_id)

                if (
                    product is None
                    or not product.is_available
                    or item.quantity > product.stock
                ):

                    locked_order.payment_status = 'Paid'
                    locked_order.razorpay_payment_id = payment_id

                    locked_order.save(
                        update_fields=[
                            'payment_status',
                            'razorpay_payment_id'
                        ]
                    )

                    messages.warning(
                        request,
                        "Payment was verified, but stock needs "
                        "manual review before fulfilment."
                    )

                    return render(
                        request,
                        'order_confirmation.html',
                        {'order': locked_order}
                    )

            for item in order_items:

                product = product_map[item.product_id]

                product.stock -= item.quantity

                product.save(
                    update_fields=['stock']
                )

            locked_order.payment_status = 'Paid'
            locked_order.razorpay_payment_id = payment_id

            locked_order.save(
                update_fields=[
                    'payment_status',
                    'razorpay_payment_id'
                ]
            )

        request.session['cart'] = {}
        request.session.modified = True

        order.refresh_from_db()

        return render(
            request,
            'order_confirmation.html',
            {'order': order}
        )

    except Exception:

        logger.exception(
            "Order confirmation failed after payment verification. "
            "Order ID: %s",
            order.id
        )

        messages.error(
            request,
            "Payment was received, but order confirmation "
            "needs review. Please contact the project administrator."
        )

        return redirect('orders:checkout')


# ==========================================
# RAZORPAY PAYMENT FAILED - FUTURE USE
# ==========================================

@login_required
@require_POST
def payment_failed(request):

    order_id = request.POST.get(
        'order_id', ''
    )

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        payment_method='Online Payment',
    )

    if order.payment_status == 'Pending':

        order.payment_status = 'Failed'

        order.save(
            update_fields=['payment_status']
        )

    messages.warning(
        request,
        "The test payment was not completed. "
        "Your cart has not been cleared."
    )

    return redirect('orders:checkout')


# ==========================================
# MY ORDERS
# ==========================================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'my_orders.html',
        {'orders': orders}
    )


# ==========================================
# ORDER DETAIL
# ==========================================

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items__product'
        ),
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'order_detail.html',
        {'order': order}
    )


# ==========================================
# CANCEL ORDER
# ==========================================

@login_required
@require_POST
def cancel_order(request, order_id):

    with transaction.atomic():

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            user=request.user
        )

        if order.status not in [
            'Pending',
            'Processing'
        ]:

            messages.error(
                request,
                "This order cannot be cancelled."
            )

            return redirect(
                'orders:order_detail',
                order_id=order.id
            )

        order_items = list(
            order.items.select_related('product')
        )

        product_ids = [
            item.product_id
            for item in order_items
        ]

        locked_products = Product.objects.select_for_update().filter(
            id__in=product_ids
        )

        product_map = {
            product.id: product
            for product in locked_products
        }

        stock_was_deducted = (
            order.payment_method == 'Cash on Delivery'
            or order.payment_status == 'Paid'
        )

        if stock_was_deducted:

            for item in order_items:

                product = product_map.get(
                    item.product_id
                )

                if product is not None:

                    product.stock += item.quantity

                    product.save(
                        update_fields=['stock']
                    )

        order.status = 'Cancelled'

        order.save(
            update_fields=['status']
        )

    messages.success(
        request,
        f"{order.order_number} has been cancelled successfully."
    )

    return redirect(
        'orders:order_detail',
        order_id=order.id
    )
