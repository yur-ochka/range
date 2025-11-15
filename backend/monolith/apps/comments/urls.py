from django.urls import path
from . import views

urlpatterns = [
    path('products/<uuid:product_id>/comments/', views.ProductCommentsListCreateView.as_view(), name='product-comments'),
    path('comments/<uuid:id>/', views.CommentDetailView.as_view(), name='comment-detail'),
]
