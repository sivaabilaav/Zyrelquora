
from django.db import models
from django.contrib.auth.models import User
from shop.models import Product


class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50,
        default='Cash on Delivery'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def order_number(self):
        if not self.pk:
            return "New Order"

        return f"ZYR-{self.created_at.year}-{self.pk:04d}"

    def __str__(self):
        return f"{self.order_number} - {self.full_name}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
