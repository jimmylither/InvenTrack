import json
from datetime import timedelta
from django.db import models
from django.db.models import Sum, Count, F
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Product, Transaction
from .serializers import (
    CategorySerializer, ProductSerializer,
    TransactionSerializer, StockOperationSerializer
)


def get_base_context():
    categories = Category.objects.all()
    low_stock_products = Product.objects.filter(
        quantity__lte=F('reorder_level')
    ).order_by('quantity')[:5]
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_value = Product.objects.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0

    recent_transactions = Transaction.objects.select_related(
        'product', 'product__category'
    )[:10]

    return {
        'categories': categories,
        'low_stock_products': low_stock_products,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_value': total_value,
        'recent_transactions': recent_transactions,
    }


def dashboard(request):
    context = get_base_context()

    stock_by_category = Category.objects.annotate(
        total_stock=Sum('products__quantity')
    ).order_by('-total_stock')[:6]

    days_30 = timezone.now() - timedelta(days=30)
    transactions_30d = Transaction.objects.filter(created_at__gte=days_30)

    transactions_by_date = transactions_30d.extra(
        select={'date': "date(created_at)"}
    ).values('date').annotate(
        total_in=Sum('quantity', filter=models.Q(transaction_type='IN')),
        total_out=Sum('quantity', filter=models.Q(transaction_type='OUT'))
    ).order_by('date')

    context.update({
        'stock_by_category': stock_by_category,
        'transactions_by_date': transactions_by_date,
    })

    return render(request, 'core/dashboard.html', context)


def products_list(request):
    context = get_base_context()

    search = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')

    products = Product.objects.select_related('category')

    if search:
        products = products.filter(
            models.Q(name__icontains=search) |
            models.Q(sku__icontains=search) |
            models.Q(category__name__icontains=search)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    if stock_filter == 'low':
        products = products.filter(quantity__lte=F('reorder_level'))
    elif stock_filter == 'out':
        products = products.filter(quantity=0)
    elif stock_filter == 'in':
        products = products.filter(quantity__gt=F('reorder_level'))

    products = products[:50]
    context.update({
        'products': products,
        'search': search,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
    })

    return render(request, 'core/products.html', context)


@require_http_methods(['GET', 'POST'])
def product_create(request):
    if request.method == 'GET':
        context = get_base_context()
        return render(request, 'core/product_form.html', context)

    data = request.POST
    product = Product(
        name=data.get('name'),
        description=data.get('description', ''),
        category_id=data.get('category'),
        quantity=int(data.get('quantity', 0)),
        reorder_level=int(data.get('reorder_level', 10)),
        unit_price=data.get('unit_price', 0),
    )
    product.save()

    if int(data.get('quantity', 0)) > 0:
        Transaction.objects.create(
            product=product,
            transaction_type='IN',
            quantity=product.quantity,
            previous_quantity=0,
            new_quantity=product.quantity,
            notes='Initial stock on creation',
        )

    return JsonResponse({'success': True, 'sku': product.sku})


@require_http_methods(['GET', 'POST'])
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        context = get_base_context()
        context['product'] = product
        return render(request, 'core/product_form.html', context)

    data = request.POST
    product.name = data.get('name')
    product.description = data.get('description', '')
    product.category_id = data.get('category')
    product.reorder_level = int(data.get('reorder_level', 10))
    product.unit_price = data.get('unit_price', 0)
    product.save()

    return JsonResponse({'success': True})


@require_http_methods(['GET', 'POST'])
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        context = {'product': product}
        return render(request, 'core/product_confirm_delete.html', context)

    product.delete()
    return JsonResponse({'success': True})


@require_http_methods(['GET', 'POST'])
def stock_operation(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        context = get_base_context()
        context['product'] = product
        return render(request, 'core/stock_form.html', context)

    data = request.POST
    trans_type = data.get('transaction_type')
    quantity = int(data.get('quantity', 0))
    notes = data.get('notes', '')

    previous = product.quantity

    if trans_type == 'IN':
        product.quantity += quantity
    elif trans_type == 'OUT':
        product.quantity = max(0, product.quantity - quantity)
    else:
        product.quantity = quantity
        quantity = abs(product.quantity - previous)

    product.save()

    Transaction.objects.create(
        product=product,
        transaction_type=trans_type,
        quantity=quantity,
        previous_quantity=previous,
        new_quantity=product.quantity,
        notes=notes,
    )

    return JsonResponse({'success': True, 'new_quantity': product.quantity})


def categories_list(request):
    context = get_base_context()

    categories = Category.objects.annotate(
        product_count=Count('products'),
        total_stock=Sum('products__quantity')
    )

    context['categories'] = categories
    return render(request, 'core/categories.html', context)


@require_http_methods(['GET', 'POST'])
def category_create(request):
    if request.method == 'GET':
        return render(request, 'core/category_form.html', get_base_context())

    data = request.POST
    category = Category.objects.create(
        name=data.get('name'),
        description=data.get('description', ''),
        color=data.get('color', '#6366F1'),
        icon=data.get('icon', 'box'),
    )

    return JsonResponse({'success': True, 'id': category.id})


@require_http_methods(['GET', 'POST'])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'GET':
        context = get_base_context()
        context['category'] = category
        return render(request, 'core/category_form.html', context)

    data = request.POST
    category.name = data.get('name')
    category.description = data.get('description', '')
    category.color = data.get('color', '#6366F1')
    category.icon = data.get('icon', 'box')
    category.save()

    return JsonResponse({'success': True})


@require_http_methods(['DELETE'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return JsonResponse({'success': True})


def ledger(request):
    context = get_base_context()

    search = request.GET.get('search', '')
    trans_type = request.GET.get('type', '')
    days = int(request.GET.get('days', 30))

    transactions = Transaction.objects.select_related(
        'product', 'product__category'
    ).order_by('-created_at')

    if search:
        transactions = transactions.filter(
            models.Q(product__name__icontains=search) |
            models.Q(product__sku__icontains=search)
        )

    if trans_type:
        transactions = transactions.filter(transaction_type=trans_type)

    if days:
        since = timezone.now() - timedelta(days=days)
        transactions = transactions.filter(created_at__gte=since)

    transactions = transactions[:100]
    context.update({
        'transactions': transactions,
        'search': search,
        'trans_type': trans_type,
        'days': days,
    })

    return render(request, 'core/ledger.html', context)


def htmx_products_table(request):
    search = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.select_related('category')

    if search:
        products = products.filter(
            models.Q(name__icontains=search) |
            models.Q(sku__icontains=search) |
            models.Q(category__name__icontains=search)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    products = products[:50]

    return render(request, 'core/partials/products_table.html', {'products': products})


def htmx_refresh_stats(request):
    context = get_base_context()
    return render(request, 'core/partials/stats.html', context)


def api_products(request):
    products = Product.objects.select_related('category')
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False)


def api_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return JsonResponse(serializer.data, safe=False)


def api_transactions(request):
    transactions = Transaction.objects.select_related('product')[:100]
    serializer = TransactionSerializer(transactions, many=True)
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(['POST'])
def api_stock_operation(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    serializer = StockOperationSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)

    product = Product.objects.get(pk=serializer.validated_data['product_id'])
    trans_type = serializer.validated_data['transaction_type']
    quantity = serializer.validated_data['quantity']
    notes = serializer.validated_data.get('notes', '')

    previous = product.quantity

    if trans_type == 'IN':
        product.quantity += quantity
    elif trans_type == 'OUT':
        product.quantity = max(0, product.quantity - quantity)
    else:
        product.quantity = quantity
        quantity = abs(product.quantity - previous)

    product.save()

    Transaction.objects.create(
        product=product,
        transaction_type=trans_type,
        quantity=quantity,
        previous_quantity=previous,
        new_quantity=product.quantity,
        notes=notes,
    )

    return JsonResponse({
        'success': True,
        'new_quantity': product.quantity,
        'sku': product.sku,
    })