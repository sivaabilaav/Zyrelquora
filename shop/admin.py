
from django.contrib import admin
from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'slug')
    ordering = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-created_at',)
