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
        fields = [
            'id', 'user', 'status', 'total_amount', 'total', 'shipping_address',
            'contact_email', 'contact_phone', 'contact_name', 'items', 'created_at', 'updated_at'
        ]

    def get_total(self, obj):
        return obj.calculate_total()


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(allow_blank=False)
    contact_email = serializers.EmailField(required=False)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    contact_name = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(child=serializers.DictField(), required=False)

    def validate_items(self, value):
        if not value:
            return []

        validated = []
        for idx, payload in enumerate(value):
            pid = payload.get('product_id')
            qty = payload.get('quantity')
            if not pid or qty in (None, ''):
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

    def validate(self, attrs):
        request = self.context.get('request')
        is_authenticated = bool(request and request.user and request.user.is_authenticated)
        if not is_authenticated and not attrs.get('contact_email'):
            raise serializers.ValidationError({'contact_email': 'Email is required for guest checkout.'})
        return attrs


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
