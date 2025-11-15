from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import serializers as drf_serializers
from .models import Comment
from .serializers import CommentSerializer
from apps.catalog.models import Product


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ProductCommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Comment.objects.filter(product_id=product_id)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            product = None
        ctx['product'] = product
        return ctx

    def perform_create(self, serializer):
        product = self.get_serializer_context().get('product')
        if product is None:
            raise drf_serializers.ValidationError({'product': 'Product not found.'})
        serializer.save()


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'id'
