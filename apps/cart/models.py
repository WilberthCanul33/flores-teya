from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.catalog.models import Product

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        # AÑADE ESTOS CONSTRAINTS PARA PREVENIR DUPLICADOS
        constraints = [
            # Un solo carrito por usuario autenticado
            models.UniqueConstraint(
                fields=['user'],
                name='unique_cart_per_user',
                condition=models.Q(user__isnull=False)
            ),
            # Un solo carrito por sesión anónima
            models.UniqueConstraint(
                fields=['session_key'],
                name='unique_cart_per_session',
                condition=models.Q(session_key__isnull=False, user__isnull=True)
            )
        ]
    
    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.email}"
        return f"Carrito anónimo {self.id}"
    
    def get_total(self):
        total = Decimal('0')
        for item in self.items.all():
            total += item.get_total()
        return total
    
    def get_total_items(self):
        """Obtiene el número total de items"""
        return self.items.count()
    
    def get_items_quantity(self):
        """Obtiene la cantidad total de productos"""
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        related_name='items', 
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total(self):
        return self.product.price * Decimal(str(self.quantity))