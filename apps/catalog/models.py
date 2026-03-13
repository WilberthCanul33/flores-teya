from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    PRESENTATION_CHOICES = [
        ('PZA', _('Piece')),
        ('KG', _('Kilogram')),
        ('BCH', _('Bag')),
        ('MZO', _('Bunch')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('name'))
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('category'))
    presentation = models.CharField(max_length=3, choices=PRESENTATION_CHOICES, default='PZA', verbose_name=_('presentation'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    properties = models.TextField(help_text=_("Nutritional properties and benefits"), verbose_name=_('properties'))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_('image'))
    stock = models.PositiveIntegerField(default=0, verbose_name=_('stock'))
    is_available = models.BooleanField(default=True, verbose_name=_('is available'))
    featured = models.BooleanField(default=False, verbose_name=_('featured'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))
    
    class Meta:
        ordering = ['name']
        verbose_name = _('product')
        verbose_name_plural = _('products')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])