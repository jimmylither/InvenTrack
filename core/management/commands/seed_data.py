from django.core.management.base import BaseCommand
from core.models import Category, Product, Transaction
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        categories_data = [
            {'name': 'Electronics', 'color': '#3B82F6', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'color': '#EC4899', 'description': 'Apparel and fashion items'},
            {'name': 'Food & Beverages', 'color': '#10B981', 'description': 'Consumable food items'},
            {'name': 'Home & Garden', 'color': '#F59E0B', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports', 'color': '#8B5CF6', 'description': 'Sporting goods and equipment'},
        ]

        categories = []
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'color': cat_data['color'], 'description': cat_data['description']}
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'Created category: {cat.name}')

        products_data = [
            {'name': 'Wireless Mouse', 'category': 0, 'quantity': 150, 'reorder_level': 20, 'unit_price': 29.99},
            {'name': 'Mechanical Keyboard', 'category': 0, 'quantity': 45, 'reorder_level': 15, 'unit_price': 89.99},
            {'name': 'USB-C Hub', 'category': 0, 'quantity': 8, 'reorder_level': 25, 'unit_price': 49.99},
            {'name': 'HD Monitor 27"', 'category': 0, 'quantity': 22, 'reorder_level': 10, 'unit_price': 299.99},
            {'name': 'Cotton T-Shirt', 'category': 1, 'quantity': 200, 'reorder_level': 50, 'unit_price': 19.99},
            {'name': 'Denim Jeans', 'category': 1, 'quantity': 5, 'reorder_level': 20, 'unit_price': 59.99},
            {'name': 'Winter Jacket', 'category': 1, 'quantity': 35, 'reorder_level': 10, 'unit_price': 129.99},
            {'name': 'Organic Coffee Beans', 'category': 2, 'quantity': 500, 'reorder_level': 100, 'unit_price': 14.99},
            {'name': 'Green Tea Box', 'category': 2, 'quantity': 320, 'reorder_level': 80, 'unit_price': 8.99},
            {'name': 'Protein Bars', 'category': 2, 'quantity': 0, 'reorder_level': 50, 'unit_price': 24.99},
            {'name': 'Garden Hose 50ft', 'category': 3, 'quantity': 28, 'reorder_level': 10, 'unit_price': 34.99},
            {'name': 'LED Light Bulbs', 'category': 3, 'quantity': 180, 'reorder_level': 40, 'unit_price': 12.99},
            {'name': 'Yoga Mat', 'category': 4, 'quantity': 65, 'reorder_level': 15, 'unit_price': 24.99},
            {'name': 'Basketball', 'category': 4, 'quantity': 42, 'reorder_level': 10, 'unit_price': 29.99},
            {'name': 'Dumbbells Set', 'category': 4, 'quantity': 12, 'reorder_level': 8, 'unit_price': 79.99},
        ]

        for prod_data in products_data:
            category = categories[prod_data['category']]
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                category=category,
                defaults={
                    'quantity': prod_data['quantity'],
                    'reorder_level': prod_data['reorder_level'],
                    'unit_price': prod_data['unit_price'],
                    'description': f'High quality {prod_data["name"]}'
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name} ({product.sku})')

                if product.quantity > 0:
                    Transaction.objects.create(
                        product=product,
                        transaction_type='IN',
                        quantity=product.quantity,
                        previous_quantity=0,
                        new_quantity=product.quantity,
                        notes='Initial stock',
                    )

        products = list(Product.objects.all())
        if products:
            for i in range(20):
                product = random.choice(products)
                trans_type = random.choice(['IN', 'OUT', 'ADJUST'])
                qty = random.randint(1, 20)
                prev = product.quantity

                if trans_type == 'IN':
                    new_qty = prev + qty
                elif trans_type == 'OUT':
                    new_qty = max(0, prev - qty)
                else:
                    new_qty = qty
                    qty = abs(new_qty - prev)

                product.quantity = new_qty
                product.save()

                Transaction.objects.create(
                    product=product,
                    transaction_type=trans_type,
                    quantity=qty,
                    previous_quantity=prev,
                    new_quantity=new_qty,
                    notes=f'Sample transaction {i+1}',
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )

            self.stdout.write(f'Created 20 sample transactions')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))