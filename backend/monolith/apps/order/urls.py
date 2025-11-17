from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<uuid:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('create-from-cart/', views.create_order_from_cart, name='order-create-from-cart'),
    path('lookup/<uuid:id>/', views.OrderStatusLookupView.as_view(), name='order-lookup'),
    path('admin/', views.OrderAdminListView.as_view(), name='order-admin-list'),
    path('admin/<uuid:id>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
]
