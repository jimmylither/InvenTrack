from rest_framework import serializers
from .models import Category, Product, Transaction


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    total_stock_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon',
                  'product_count', 'total_stock_value', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    total_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'category', 'category_id',
                  'category_name', 'quantity', 'reorder_level', 'unit_price',
                  'stock_status', 'total_value', 'image', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    change_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'product', 'product_sku', 'product_name', 'transaction_type',
                  'quantity', 'previous_quantity', 'new_quantity', 'change_amount',
                  'notes', 'created_at']


class StockOperationSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    transaction_type = serializers.ChoiceField(choices=Transaction.TRANSACTION_TYPES)
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
