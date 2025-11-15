from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('created_at',)
