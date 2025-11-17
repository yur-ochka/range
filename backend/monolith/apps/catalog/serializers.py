from rest_framework import serializers
from .models import Category, Product, Favorite, Rating


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source='category.id', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'brand', 'price',
            'image_url', 'alt_text', 'stock_quantity', 'in_stock', 'rating', 'rating_count',
            'category_id', 'category_title', 'created_at', 'is_favorite'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


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
    recommendations = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['category', 'recommendations', 'user_rating']

    def get_recommendations(self, obj):
        queryset = (
            Product.objects.filter(category=obj.category, in_stock=True)
            .exclude(pk=obj.pk)
            .order_by('-created_at')[:4]
        )
        return ProductSerializer(queryset, many=True, context=self.context).data

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            if rating:
                return RatingSerializer(rating).data
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'brand', 'price', 'category',
            'image_url', 'alt_text', 'stock_quantity', 'in_stock'
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'product_id', 'created_at']
        read_only_fields = ['id', 'product', 'created_at']

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product does not exist.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        user = validated_data.get('user') or request.user
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(pk=product_id)
        favorite, created = Favorite.objects.get_or_create(user=user, product=product)
        if not created:
            raise serializers.ValidationError({'detail': 'Product already in favorites.'})
        return favorite


class RatingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'score', 'review', 'user_id', 'user_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'user_email', 'created_at', 'updated_at']

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
