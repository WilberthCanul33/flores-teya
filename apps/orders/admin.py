from django.contrib import admin
from .models import Order, OrderItem, OrderHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'product_name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 
        'user', 
        'get_total_display', 
        'get_status_display',
        'get_delivery_method_display',
        'pickup_date',  # 👈 AGREGADO
        'created_at'
    ]
    list_filter = ['status', 'delivery_method', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'shipping_address']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Información de la orden', {
            'fields': ('order_number', 'user', 'status', 'notes')
        }),
        ('Método de entrega', {
            'fields': ('delivery_method', 'pickup_point', 'pickup_date', 'estimated_delivery_date', 'delivery_time_slot'),  # 👈 AGREGADO pickup_date
        }),
        ('Dirección de envío', {
            'fields': ('shipping_address', 'shipping_phone'),
            'description': 'Dirección completa de entrega (Mérida, Yucatán)',
            'classes': ('wide',)
        }),
        ('Información de pago', {
            'fields': ('payment_method', 'payment_status', 'payment_reference', 'paypal_order_id'),  # 👈 AGREGADO paypal_order_id
        }),
        ('Totales', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_display(self, obj):
        return f"${obj.total}"
    get_total_display.short_description = 'Total'
    
    # Personalizar la visualización de pickup_date
    def pickup_date(self, obj):
        if obj.pickup_date:
            return obj.pickup_date.strftime('%d/%m/%Y')
        return '-'
    pickup_date.short_description = 'Fecha de recogida'
    pickup_date.admin_order_field = 'pickup_date'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'get_total_display']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = ['product', 'product_name', 'price']
    
    def get_total_display(self, obj):
        return f"${obj.get_total()}"
    get_total_display.short_description = 'Total'

@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'get_status_display', 'created_by', 'created_at']
    list_filter = ['status']
    readonly_fields = ['order', 'status', 'notes', 'created_by', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False