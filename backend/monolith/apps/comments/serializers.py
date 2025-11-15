from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    product_id = serializers.UUIDField(source='product.id', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'product_id', 'user_id', 'user_username', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'product_id', 'user_id', 'user_username', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        product = self.context.get('product')
        if request is None or not request.user or request.user.is_anonymous:
            raise serializers.ValidationError('Authentication required to create comments.')
        if product is None:
            raise serializers.ValidationError('Product context is required to create a comment.')
        comment = Comment.objects.create(
            product=product,
            user=request.user,
            text=validated_data.get('text', '')
        )
        return comment
