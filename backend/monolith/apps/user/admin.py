from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Register the custom User model in admin reusing Django's UserAdmin."""
    model = User
    list_display = (
        'email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    # reuse the base fieldsets and add_fieldsets - they work for AbstractUser
    fieldsets = DjangoUserAdmin.fieldsets
    add_fieldsets = DjangoUserAdmin.add_fieldsets


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__email', 'user__username', 'phone')
