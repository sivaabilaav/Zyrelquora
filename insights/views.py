
from django.shortcuts import render
from shop.models import Product, Category
from django.db.models import Count, Q


def shopping_insights(request):

    # Overview Statistics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    available_products = Product.objects.filter(
        is_available=True,
        stock__gt=0
    ).count()

    out_of_stock_products = Product.objects.filter(
        Q(is_available=False) | Q(stock__lte=0)
    ).count()

    # Category Distribution Chart
    categories = Category.objects.annotate(
        product_count=Count('products')
    )

    category_labels = [
        category.name for category in categories
    ]

    category_values = [
        category.product_count for category in categories
    ]

    # Product Price Comparison Chart
    products = Product.objects.order_by('-price')[:10]

    product_labels = [
        product.name for product in products
    ]

    product_prices = [
        float(product.price) for product in products
    ]

    # Stock Overview Chart
    stock_labels = [
        'Available',
        'Out of Stock'
    ]

    stock_values = [
        available_products,
        out_of_stock_products
    ]

    # Dashboard Context
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'available_products': available_products,
        'out_of_stock_products': out_of_stock_products,
        'category_labels': category_labels,
        'category_values': category_values,
        'product_labels': product_labels,
        'product_prices': product_prices,
        'stock_labels': stock_labels,
        'stock_values': stock_values,
    }

    return render(request, 'insights.html', context)
