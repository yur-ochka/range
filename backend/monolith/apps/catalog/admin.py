from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'image_preview']

    fieldsets = (
        ('Category Info', {
            'fields': ('title', 'description', 'image_url', 'alt_text', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def products_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:catalog_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} products</a>', url, count)
    products_count.short_description = 'Products Count'

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-width: 150px; border-radius: 6px; object-fit: cover;" />',
                obj.image_url
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'title', 'category', 'price',
        'stock_quantity', 'in_stock', 'rating', 'created_at'
    ]
    list_filter = ['category', 'in_stock', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['price', 'in_stock', 'rating']
    readonly_fields = ['created_at', 'image_preview_large']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'in_stock', 'rating'),
        }),
        ('Image', {
            'fields': ('image_url', 'alt_text', 'image_preview_large'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return "No Image"
    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: contain;" />',
                obj.image_url
            )
        return "No Image"
    image_preview_large.short_description = 'Image Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

    # Actions
    actions = ['mark_in_stock', 'mark_out_of_stock']

    def mark_in_stock(self, request, queryset):
        count = queryset.update(in_stock=True)
        self.message_user(request, f'{count} products marked as "In Stock".')
    mark_in_stock.short_description = "Mark selected products as In Stock"

    def mark_out_of_stock(self, request, queryset):
        count = queryset.update(in_stock=False)
        self.message_user(request, f'{count} products marked as "Out of Stock".')
    mark_out_of_stock.short_description = "Mark selected products as Out of Stock"
