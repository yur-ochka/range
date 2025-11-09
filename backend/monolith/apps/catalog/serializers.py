from rest_framework import serializers
from .models import Category, Product


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source='category.id', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price',
            'image_url', 'alt_text', 'stock_quantity', 'in_stock', 'rating',
            'category_id', 'category_title', 'created_at'
        ]


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'title', 'description',
            'image_url', 'alt_text', 'products_count',
            'products', 'created_at'
        ]

    def get_products_count(self, obj):
        return obj.products.count()


class ProductDetailSerializer(ProductSerializer):
    category = CategorySerializer(read_only=True)


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category',
            'image_url', 'alt_text', 'stock_quantity', 'in_stock', 'rating'
        ]
