from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import secrets

class User(AbstractUser):
    """Modelo de usuario personalizado"""
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # NUEVOS CAMPOS DE DIRECCIÓN - SOLO MÉRIDA
    colonia = models.CharField(max_length=100, blank=True, verbose_name='Colonia')
    calle = models.CharField(max_length=200, blank=True, verbose_name='Calle')
    numero_casa = models.CharField(max_length=20, blank=True, verbose_name='Número de casa')
    entre_calles = models.CharField(max_length=200, blank=True, verbose_name='Entre calles')
    referencias = models.TextField(blank=True, verbose_name='Referencias')
    
    # Eliminamos los campos antiguos: address, city, state, postal_code
    
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Para preferencias de comunicación
    receive_offers = models.BooleanField(default=True)
    
    # NUEVOS CAMPOS PARA VERIFICACIÓN DE EMAIL
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Para seguimiento
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    def generate_verification_token(self):
        """Genera un token único para verificación de email"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_token
    
    def verify_email(self, token):
        """Verifica el email si el token es correcto"""
        if self.email_verification_token == token:
            self.is_email_verified = True
            self.email_verification_token = None
            self.save()
            return True
        return False
    
    def get_full_address(self):
        """Devuelve la dirección completa formateada"""
        parts = []
        if self.calle:
            parts.append(f"Calle {self.calle}")
        if self.numero_casa:
            parts.append(f"#{self.numero_casa}")
        if self.colonia:
            parts.append(f"Col. {self.colonia}")
        if self.entre_calles:
            parts.append(f"entre {self.entre_calles}")
        
        address = ", ".join(parts) if parts else ""
        
        if self.referencias:
            address += f" (Ref: {self.referencias})"
        
        return address or "Dirección no especificada"