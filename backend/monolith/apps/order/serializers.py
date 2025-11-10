from rest_framework import serializers
from .models import Order, OrderItem
from apps.catalog.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_title', 'quantity', 'unit_price', 'subtotal', 'added_at']

    subtotal = serializers.SerializerMethodField()

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_amount', 'total', 'shipping_address', 'items', 'created_at', 'updated_at']

    def get_total(self, obj):
        return obj.calculate_total()


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(allow_blank=True, required=False)
    items = serializers.ListField(child=serializers.DictField(), min_length=1)

    def validate_items(self, value):
        # expect list of {"product_id": uuid, "quantity": int}
        validated = []
        for idx, it in enumerate(value):
            pid = it.get('product_id')
            qty = it.get('quantity')
            if not pid or not qty:
                raise serializers.ValidationError(f'item[{idx}] missing product_id or quantity')
            try:
                product = Product.objects.get(id=pid)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f'item[{idx}] product not found')
            try:
                qty = int(qty)
            except (ValueError, TypeError):
                raise serializers.ValidationError(f'item[{idx}] quantity must be integer')
            if qty <= 0:
                raise serializers.ValidationError(f'item[{idx}] quantity must be > 0')
            validated.append({'product': product, 'quantity': qty})
        return validated
