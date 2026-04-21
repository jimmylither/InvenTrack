import random
import string
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


def generate_sku():
    chars = ''.join(random.choices(string.digits, k=5))
    return f'INV-{chars}'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    color = models.CharField(max_length=7, default='#6366F1')
    icon = models.CharField(max_length=50, default='box')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_product_count(self):
        return self.products.count()

    def get_total_stock_value(self):
        total = sum(p.quantity * p.unit_price for p in self.products.all())
        return total


class Product(models.Model):
    sku = models.CharField(max_length=10, unique=True, default=generate_sku, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category', 'quantity']),
        ]

    def __str__(self):
        return f'{self.sku} - {self.name}'

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.reorder_level:
            return 'low_stock'
        return 'in_stock'

    @property
    def total_value(self):
        return self.quantity * self.unit_price


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUST', 'Adjustment'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f'{self.product.sku} - {self.transaction_type} - {self.quantity}'

    @property
    def change_amount(self):
        return self.new_quantity - self.previous_quantity