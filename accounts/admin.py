from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'phone', 'user_type', 'is_verified', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'phone')
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        ('Profile', {'fields': ('user_type', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'phone', 'password1', 'password2', 'is_staff', 'is_superuser'),
            },
        ),
    )
    readonly_fields = ('created_at',)
