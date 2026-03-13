from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('is_email_verified', 'is_staff', 'is_active', 'receive_offers')
    search_fields = ('email', 'first_name', 'last_name', 'phone', 'colonia', 'calle')
    ordering = ('email',)
    
    # Agrupar campos en el formulario de edición
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')
        }),
        
        ('Dirección de entrega (Mérida)', {
            'fields': (
                'colonia', 
                'calle', 
                'numero_casa', 
                'entre_calles', 
                'referencias'
            ),
            'description': 'Los pedidos solo se entregan en Mérida, Yucatán'
        }),
        
        ('Preferencias', {
            'fields': ('receive_offers',)
        }),
        
        ('Verificación', {
            'fields': ('is_email_verified', 'email_verification_token', 'email_verification_sent_at')
        }),
        
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('created_at', 'updated_at', 'email_verification_token', 'email_verification_sent_at')
    
    # Configuración para crear nuevos usuarios
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )

admin.site.register(User, CustomUserAdmin)