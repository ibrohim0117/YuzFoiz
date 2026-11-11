from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'image_preview', 'image_status', 'is_staff')
    list_filter = ('image_status',) + BaseUserAdmin.list_filter
    readonly_fields = ('image_preview',)
    actions = ('approve_images',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rasm', {'fields': ('image', 'image_preview', 'image_status', 'rejection_reason')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Rasm', {'fields': ('image', 'image_status', 'rejection_reason')}),
    )

    @admin.display(description='Ko\'rinish')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;">', obj.image.url)
        return '—'

    @admin.action(description='Tanlangan rasmlarni tasdiqlash')
    def approve_images(self, request, queryset):
        updated = queryset.update(image_status=User.ImageStatus.APPROVED, rejection_reason='')
        self.message_user(request, f'{updated} ta rasm tasdiqlandi.', messages.SUCCESS)
