from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Category, Product, Favorite, Rating
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    FavoriteSerializer, RatingSerializer
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
    ordering_fields = ['title', 'price', 'created_at', 'rating']
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

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        sort = self.request.query_params.get('sort')
        if sort:
            sort_map = {
                'price_asc': 'price',
                'price_desc': '-price',
                'newest': '-created_at',
                'oldest': 'created_at',
                'rating_desc': '-rating',
                'rating_asc': 'rating',
                'title_asc': 'title',
                'title_desc': '-title',
            }
            ordering = sort_map.get(sort.lower())
            if ordering:
                queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('ratings', 'favorited_by')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer


class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('product', 'product__category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDestroyView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        product_id = self.kwargs['product_id']
        return get_object_or_404(Favorite, user=self.request.user, product_id=product_id)


class ProductRatingListView(generics.ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        product_id = self.kwargs['pk']
        return Rating.objects.filter(product_id=product_id).select_related('user', 'product')


class ProductRatingView(generics.GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_product(self):
        return get_object_or_404(Product, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        product = self.get_product()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={
                'score': serializer.validated_data['score'],
                'review': serializer.validated_data.get('review', ''),
            }
        )
        product.update_rating_stats()
        output_serializer = self.get_serializer(rating)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        product = self.get_product()
        rating = Rating.objects.filter(user=request.user, product=product).first()
        if not rating:
            return Response({'detail': 'Rating not found.'}, status=status.HTTP_404_NOT_FOUND)
        rating.delete()
        product.update_rating_stats()
        return Response(status=status.HTTP_204_NO_CONTENT)

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