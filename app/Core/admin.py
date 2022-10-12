"""
Personalización Django admin
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from Core import models


class UserAdmin(BaseUserAdmin):
    """Define las paginas admin para Usuarios"""
    ordering = ['id']
    list_display = ['correo', 'nombre', 'is_superuser', 'is_active']
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'nombre',
                    'correo',
                    'password'
                )
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (
            _('Fechas Importantes'),
            {
                'fields': (
                    'last_login',
                )
            }
        )
    )

    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': (
                    'correo',
                    'password1',
                    'password2',
                    'nombre',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
    )
    readonly_fields = ['last_login']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Receta)
