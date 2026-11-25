
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'full_name',
        'user',
        'total_amount',
        'payment_method',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'full_name',
        'email',
        'phone',
        'user__username',
    )

    readonly_fields = ('created_at',)

    inlines = [OrderItemInline]
