from django.urls import path
from . import views

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Product endpoints
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<uuid:id>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Product actions
    path('products/<uuid:product_id>/reserve/', views.reserve_product, name='reserve-product'),
    path('products/<uuid:product_id>/release/', views.release_product, name='release-product'),
    path('products/<uuid:product_id>/check-availability/', views.check_availability, name='check-availability'),
]
