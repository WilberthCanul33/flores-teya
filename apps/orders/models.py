from django.db import models
from django.conf import settings
from apps.catalog.models import Product
from decimal import Decimal

class Order(models.Model):
    """Modelo para las órdenes de compra"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
        ('ready_for_pickup', 'Listo para recoger'),
        ('picked_up', 'Recogido'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
    ('paypal', 'PayPal'),  # Solo PayPal
    ]
    
    # NUEVO: Métodos de entrega
    DELIVERY_METHOD_CHOICES = [
        ('pickup', 'Recoger en punto físico'),
        ('home_delivery', 'Envío a domicilio'),
    ]
    
    PICKUP_POINT_CHOICES = [
        ('mercado', '📍 Punto 1 – Mercado'),
        ('segundo_lugar', '📍 Punto 2 – Segundo lugar físico'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Usuario'
    )
    
    # NUEVOS CAMPOS
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES,
        default='home_delivery',
        verbose_name='Método de entrega'
    )
    
    pickup_point = models.CharField(
        max_length=20,
        choices=PICKUP_POINT_CHOICES,
        blank=True,
        null=True,
        verbose_name='Punto de recogida'
    )

    # NUEVO: Fecha de recogida seleccionada por el usuario
    pickup_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de recogida'
    )
    
    estimated_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha estimada de entrega'
    )
    
    delivery_time_slot = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Horario de entrega',
        default='9:00 AM - 6:00 PM'
    )
    
    # Información de la orden
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de orden'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Información de envío
    shipping_address = models.TextField(verbose_name='Dirección de envío', blank=True)
    shipping_city = models.CharField(max_length=100, verbose_name='Ciudad', blank=True)
    shipping_state = models.CharField(max_length=100, verbose_name='Estado', blank=True)
    shipping_postal_code = models.CharField(max_length=10, verbose_name='Código Postal', blank=True)
    shipping_phone = models.CharField(max_length=15, verbose_name='Teléfono de contacto', blank=True)
    
    # Información de pago
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='card',
        verbose_name='Método de pago'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Estado del pago'
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia de pago'
    )

    # NUEVO CAMPO PARA PAYPAL
    paypal_order_id = models.CharField(
      max_length=100,
      blank=True,
      null=True,
      verbose_name='ID de orden PayPal'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal'
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Costo de envío'
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='IVA'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total'
    )
    
    # Metadatos
    notes = models.TextField(
        blank=True,
        verbose_name='Notas adicionales'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Orden #{self.order_number} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generar número de orden único
            last_order = Order.objects.all().order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.order_number = f"ORD-{new_number:06d}"
        super().save(*args, **kwargs)
    
    def get_pickup_point_details(self):
        """Obtener detalles del punto de recogida"""
        points = {
            'mercado': {
                'name': 'Mercado',
                'address': 'Av. Principal #123, Centro',
                'map_url': 'https://maps.google.com/?q=Mercado+Central',
                'schedule': 'Solo sábados de 8:00 AM a 1:00 PM',
                'icon': 'fa-store'
            },
            'segundo_lugar': {
                'name': 'Segundo lugar físico',
                'address': 'Calle Secundaria #456, Colonia Centro',
                'map_url': 'https://maps.google.com/?q=Segundo+Lugar',
                'schedule': 'Lunes a sábado de 7:00 AM a 5:00 PM',
                'icon': 'fa-building'
            }
        }
        return points.get(self.pickup_point, {})


class OrderItem(models.Model):
    """Modelo para los items de una orden"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Orden'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    product_name = models.CharField(
        max_length=200,
        verbose_name='Nombre del producto'
    )  # Guardamos el nombre por si el producto cambia después
    
    class Meta:
        verbose_name = 'Item de orden'
        verbose_name_plural = 'Items de orden'
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    def get_total(self):
        return self.price * Decimal(str(self.quantity))


class OrderHistory(models.Model):
    """Historial de cambios de estado de la orden"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Orden'
    )
    status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES,
        verbose_name='Estado'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    class Meta:
        verbose_name = 'Historial de orden'
        verbose_name_plural = 'Historial de órdenes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()} - {self.created_at}"