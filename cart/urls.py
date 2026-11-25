from django.urls import path
from . import views

# Cart Application URL Patterns
urlpatterns = [

    # Display Cart Page
    path('', views.cart_view, name='cart'),

    # Add Product to Cart
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Update Product Quantity
    path('update/<int:product_id>/', views.update_quantity, name='update_quantity'),

    # Remove Individual Product from Cart
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Clear All Products from Cart
    path('clear/', views.clear_cart, name='clear_cart'),

]