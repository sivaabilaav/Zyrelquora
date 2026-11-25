
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal

from shop.models import Product



def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('products')

    product = get_object_or_404(Product, id=product_id)

    # Check product availability
    if not product.is_available or product.stock <= 0:
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect('products')

    cart = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key in cart:
        current_quantity = int(cart[product_key]['quantity'])

        # Check available stock before increasing quantity
        if current_quantity >= product.stock:
            messages.warning(
                request,
                f"Only {product.stock} units of {product.name} are available."
            )
            return redirect('cart')

        cart[product_key]['quantity'] = current_quantity + 1

    else:
        cart[product_key] = {
            'name': product.name,
            'price': str(product.price),
            'image': product.image,
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f"{product.name} added to your cart!")
    return redirect('cart')


# DISPLAY CART WITH STOCK VALIDATION
def cart_view(request):

    cart = request.session.get('cart', {})

    total_price = Decimal('0.00')
    total_items = 0

    # Check every product currently in the cart
    for product_key in list(cart.keys()):

        product = Product.objects.filter(id=product_key).first()

        # Remove products that no longer exist
        if product is None:
            del cart[product_key]
            messages.warning(
                request,
                "A product in your cart is no longer available and has been removed. Please continue shopping to explore other products."
            )
            continue

        # Remove products that are unavailable or out of stock
        if not product.is_available or product.stock <= 0:
            del cart[product_key]
            messages.warning(
                request,
                f"{product.name} is out of stock and has been removed from your cart. Please explore our products for other available choices."
            )
            continue

        item = cart[product_key]
        quantity = int(item['quantity'])

        # Reduce quantity if it exceeds the current stock
        if quantity > product.stock:
            quantity = product.stock

            messages.warning(
                request,
                f"The quantity of {product.name} has been adjusted to {product.stock} because of limited stock."
            )

        # Refresh product information from the database
        item['name'] = product.name
        item['price'] = str(product.price)
        item['image'] = product.image
        item['quantity'] = quantity
        # Set stock status for cart display
        if product.stock <= 3:
            item['stock_status'] = f"Only {product.stock} left in stock"
            item['stock_class'] = 'limited-stock'
        else:
            item['stock_status'] = 'In Stock'
            item['stock_class'] = 'available-stock'

        # Calculate subtotal
        price = Decimal(str(product.price))
        item['subtotal'] = str(price * quantity)

        total_price += Decimal(item['subtotal'])
        total_items += quantity

    # Save the validated cart in the session
    request.session['cart'] = cart
    request.session.modified = True

    context = {
        'cart_items': cart,
        'total_price': total_price,
        'total_items': total_items,
    }

    return render(request, 'cart.html', context)

# UPDATE PRODUCT QUANTITY
def update_quantity(request, product_id):
    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key not in cart:
        return redirect('cart')

    product = get_object_or_404(Product, id=product_id)

    action = request.POST.get('action')
    current_quantity = int(cart[product_key]['quantity'])

    if action == 'increase':
        if not product.is_available or current_quantity >= product.stock:
            messages.warning(
                request,
                f"Only {product.stock} units of {product.name} are available."
            )
        else:
            cart[product_key]['quantity'] = current_quantity + 1

    elif action == 'decrease':
        cart[product_key]['quantity'] = max(1, current_quantity - 1)

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


# REMOVE PRODUCT FROM CART
def remove_from_cart(request, product_id):

    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key in cart:

        del cart[product_key]

        request.session['cart'] = cart
        request.session.modified = True

        messages.success(
            request,
            'Product removed from your cart!'
        )

    return redirect('cart')


# CLEAR ENTIRE CART
def clear_cart(request):

    if request.method != 'POST':
        return redirect('cart')

    request.session['cart'] = {}
    request.session.modified = True

    messages.success(
        request,
        'Your cart has been cleared!'
    )

    return redirect('cart')