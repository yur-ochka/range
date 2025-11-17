from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Avg, Count
import uuid

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['title']

    def __str__(self):
        return self.title


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    rating_count = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def reserve_quantity(self, quantity):
        """Reserved specified quantity if available"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            if self.stock_quantity == 0:
                self.in_stock = False
            self.save()
            return True
        return False

    def release_quantity(self, quantity):
        """Release specified quantity back to stock"""
        self.stock_quantity += quantity
        if self.stock_quantity > 0:
            self.in_stock = True
        self.save()

    def update_rating_stats(self):
        """Recalculate average rating and count based on related ratings."""
        aggregate = self.ratings.aggregate(avg=Avg('score'), count=Count('id'))
        avg = aggregate['avg'] or 0
        count = aggregate['count'] or 0
        if count:
            avg_decimal = Decimal(str(avg)).quantize(Decimal('0.01'))
        else:
            avg_decimal = Decimal('0.00')
        self.rating = avg_decimal
        self.rating_count = count
        self.save(update_fields=['rating', 'rating_count'])


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} -> {self.product.title}"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Rating {self.score} for {self.product.title} by {self.user.email}"
