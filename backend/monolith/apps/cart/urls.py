from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart-detail'),
    path('items/', views.CartItemAddView.as_view(), name='cart-items-add'),
    path('items/<uuid:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
]
