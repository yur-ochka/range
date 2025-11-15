from django.db import models
import uuid
from django.conf import settings


class Comment(models.Model):
    """User comments for products."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Use the app label 'catalog' for the string reference (AppConfig.name is 'apps.catalog')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.product}"
