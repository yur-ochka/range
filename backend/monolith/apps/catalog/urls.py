from django.urls import include, path
from . import views

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:id>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Product endpoints
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<uuid:pk>/ratings/', views.ProductRatingListView.as_view(), name='product-rating-list'),
    path('products/<uuid:pk>/rate/', views.ProductRatingView.as_view(), name='product-rate'),

    # Product actions
    path('products/<uuid:product_id>/reserve/', views.reserve_product, name='reserve-product'),
    path('products/<uuid:product_id>/release/', views.release_product, name='release-product'),
    path('products/<uuid:product_id>/check-availability/', views.check_availability, name='check-availability'),

    # Favorites
    path('favorites/', views.FavoriteListCreateView.as_view(), name='favorite-list'),
    path('favorites/<uuid:product_id>/', views.FavoriteDestroyView.as_view(), name='favorite-delete'),

    #Coments
    path('', include('apps.comments.urls')),
]
