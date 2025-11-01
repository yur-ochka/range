from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer
)

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(in_stock=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

@api_view(['POST'])
def reserve_product(request, product_id):
    """Product reservation endpoint"""
    try:
        product = Product.objects.get(id=product_id)
        quantity = int(request.data.get('quantity', 1))

        if product.reserve_quantity(quantity):
            return Response({
                'success': True,
                'message': f'{quantity} units of goods reserved.',
                'remaining_stock': product.stock_quantity
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Insufficient quantity of goods in stock.'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Product.DoesNotExist:
        return Response({'error': 'Product not found .'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def release_product(request, product_id):
    """Release of product reserve"""
    try:
        product = Product.objects.get(id=product_id)
        quantity = int(request.data.get('quantity', 1))
        product.release_quantity(quantity)
        return Response({
            'success': True,
            'message': f'{quantity} units returned to stock.',
            'new_stock': product.stock_quantity
        }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def check_availability(request, product_id):
    """Check product availability"""
    try:
        product = Product.objects.get(id=product_id)
        return Response({
            'product_id': str(product.id),
            'title': product.title,
            'in_stock': product.in_stock,
            'stock_quantity': product.stock_quantity
        }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
