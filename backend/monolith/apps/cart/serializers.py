from rest_framework import serializers
from .models import Cart, CartItem
from apps.catalog.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_title', 'quantity', 'unit_price', 'added_at']


class CartItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'items', 'total', 'created_at', 'updated_at']

    def get_total(self, obj):
        return obj.total()
