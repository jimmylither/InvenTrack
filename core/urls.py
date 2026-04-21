from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products', views.products_list, name='products'),
    path('products/new', views.product_create, name='product_create'),
    path('products/<int:pk>/edit', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete', views.product_delete, name='product_delete'),
    path('products/<int:pk>/stock', views.stock_operation, name='stock_operation'),
    path('categories', views.categories_list, name='categories'),
    path('categories/new', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete', views.category_delete, name='category_delete'),
    path('ledger', views.ledger, name='ledger'),
    path('htmx/products-table', views.htmx_products_table, name='htmx_products_table'),
    path('htmx/refresh-stats', views.htmx_refresh_stats, name='htmx_refresh_stats'),
    path('api/products', views.api_products, name='api_products'),
    path('api/categories', views.api_categories, name='api_categories'),
    path('api/transactions', views.api_transactions, name='api_transactions'),
    path('api/stock-operation', views.api_stock_operation, name='api_stock_operation'),
]