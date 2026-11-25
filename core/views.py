
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from shop.models import Product


# Home Page
@login_required
def home(request):
    featured_products = Product.objects.select_related(
        'category'
    ).order_by('-created_at')[:4]

    context = {
        'featured_products': featured_products
    }

    return render(request, 'home.html', context)


# About Page
def about(request):
    return render(request, 'about.html')

# Custom 404 Error Page
def custom_404(request, exception):
    return render(request, '404.html', status=404)