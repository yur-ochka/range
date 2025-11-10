from rest_framework import serializers
from .models import PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'order', 'user', 'amount', 'currency', 'status',
            'provider', 'provider_id', 'metadata', 'created_at', 'updated_at'
        ]


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()

    def validate(self, attrs):
        # keep validation minimal here; view will enforce order ownership
        return attrs


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = None  # set dynamically to avoid import cycle
        fields = [
            'id', 'payment', 'amount', 'currency', 'status',
            'provider', 'provider_refund_id', 'metadata', 'created_at', 'updated_at'
        ]


class RefundCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('amount must be positive')
        return value
