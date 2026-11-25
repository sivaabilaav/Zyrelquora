
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Category, Review
from .forms import ReviewForm


def product_list(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    products = Product.objects.select_related('category').all()

    # Search products
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Filter by category
    if selected_category:
        products = products.filter(
            category__name=selected_category
        )

    # Sort products
    if sort_by == 'price_low':
        products = products.order_by('price')

    elif sort_by == 'price_high':
        products = products.order_by('-price')

    elif sort_by == 'name_asc':
        products = products.order_by('name')

    elif sort_by == 'name_desc':
        products = products.order_by('-name')

    else:
        products = products.order_by('name')

    # Get categories
    categories = Category.objects.order_by('name').values_list(
        'name', flat=True
    )

    # Pagination - 5 products per page
    paginator = Paginator(products, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'sort_by': sort_by,
    }

    return render(request, 'products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug
    )

    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
        stock__gt=0
    ).exclude(
        id=product.id
    ).select_related('category').order_by('name')[:4]

    # Recently viewed products
    recently_viewed_ids = request.session.get(
        'recently_viewed',
        []
    )

    previous_ids = [
        product_id for product_id in recently_viewed_ids
        if product_id != product.id
    ]

    recent_products_queryset = Product.objects.filter(
        id__in=previous_ids,
        is_available=True,
        stock__gt=0
    ).select_related('category')

    recent_products = sorted(
        recent_products_queryset,
        key=lambda item: previous_ids.index(item.id)
    )[:4]

    request.session['recently_viewed'] = (
        [product.id] + previous_ids
    )[:6]

    # Product reviews
    reviews = Review.objects.filter(
        product=product
    ).select_related('user')

    average_rating = reviews.aggregate(
        average=Avg('rating')
    )['average']

    review_count = reviews.count()

    # Review form
    review_form = ReviewForm()

    # Check whether the logged-in user has already reviewed
    user_has_reviewed = False

    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'recent_products': recent_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
    }

    return render(request, 'product_detail.html', context)


@login_required
def submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Only accept POST requests
    if request.method != 'POST':
        return redirect('shop:product_detail', slug=slug)

    # Prevent duplicate reviews
    if Review.objects.filter(
        product=product,
        user=request.user
    ).exists():
        messages.warning(
            request,
            'You have already reviewed this product.'
        )
        return redirect('shop:product_detail', slug=slug)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        messages.success(
            request,
            'Your review has been submitted successfully!'
        )

    else:
        messages.error(
            request,
            'Please enter a valid review and rating.'
        )

    return redirect('shop:product_detail', slug=slug)
