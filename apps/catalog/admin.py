from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Productos'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Columnas que se muestran en la lista de productos
    list_display = [
        'name', 
        'category', 
        'price', 
        'presentation',
        'stock', 
        'is_available', 
        'featured',
        'image_preview'
    ]
    
    # Filtros laterales
    list_filter = ['category', 'is_available', 'featured', 'presentation']
    
    # Campos que se pueden buscar
    search_fields = ['name', 'properties']
    
    # Campos que se pueden editar directamente desde la lista
    list_editable = ['price', 'stock', 'is_available', 'featured']
    
    # Orden por defecto
    ordering = ['name']
    
    # Paginación
    list_per_page = 25
    
    # Preparación de campos para el formulario
    prepopulated_fields = {'slug': ('name',)}
    
    # Campos de solo lectura
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'slug', 'category', 'presentation')
        }),
        ('Precio y stock', {
            'fields': ('price', 'stock', 'is_available', 'featured')
        }),
        ('Descripción', {
            'fields': ('properties',),
            'classes': ('wide',),
        }),
        ('Imagen', {
            'fields': ('image', 'image_preview'),
            'description': 'Sube una imagen del producto (formatos: JPG, PNG)'
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Vista previa de la imagen
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista previa'
    
    # Acciones personalizadas
    actions = ['make_available', 'make_unavailable', 'make_featured']
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} productos marcados como disponibles.')
    make_available.short_description = "Marcar como disponibles"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} productos marcados como no disponibles.')
    make_unavailable.short_description = "Marcar como no disponibles"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} productos marcados como destacados.')
    make_featured.short_description = "Marcar como destacados"