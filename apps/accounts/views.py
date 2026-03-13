from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
from .models import User  # ¡IMPORTANTE! Agrega esta importación

def send_verification_email(user, request):
    """Envía email de verificación al usuario"""
    token = user.generate_verification_token()
    
    # Construir link de verificación
    verification_link = f"{settings.SITE_URL}/accounts/verificar/{token}/"
    
    # Imprimir en consola para DEBUG (solo tú lo ves)
    print(f"\n🔗 LINK DE VERIFICACIÓN (solo para desarrollo): {verification_link}\n")
    
    # Preparar email
    subject = 'Verifica tu correo electrónico - Flores Teya'
    html_message = render_to_string('accounts/email/verification_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    plain_message = strip_tags(html_message)
    
    try:
        # Enviar email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"📧 Email enviado a {user.email}")
    except Exception as e:
        print(f"❌ Error enviando email: {e}")

def register_view(request):
    """Vista de registro de usuarios con verificación de email"""
    if request.user.is_authenticated:
        return redirect('catalog:catalog')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.is_email_verified = False
            user.save()
            
            # Enviar email de verificación
            send_verification_email(user, request)
            
            # 🔥 ELIMINA ESTE BLOQUE QUE MUESTRA EL LINK DIRECTAMENTE
            # if settings.DEBUG:
            #     messages.success(request, 
            #         '¡Registro exitoso! Haz clic en este link para verificar: '
            #         f'<a href="{settings.SITE_URL}/accounts/verificar/{user.email_verification_token}/">'
            #         'Verificar ahora</a>'
            #     )
            # else:
            #     messages.success(request, 
            #         '¡Registro exitoso! Por favor revisa tu correo para verificar tu cuenta.')
            
            # ✅ NUEVO: Mensaje genérico para TODOS los entornos
            messages.success(request, 
                '¡Registro exitoso! Por favor revisa tu correo para verificar tu cuenta. '
                'El enlace de verificación expirará en 24 horas.'
            )
            
            return redirect('accounts:login')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Vista de inicio de sesión con verificación de email"""
    if request.user.is_authenticated:
        return redirect('catalog:catalog')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Verificar si el email está verificado
                if not user.is_email_verified:
                    messages.warning(request, 
                        'Por favor verifica tu correo electrónico antes de iniciar sesión. '
                        '<a href="{}">Reenviar email</a>'.format(reverse('accounts:resend_verification')))
                    return redirect('accounts:login')
                
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo {user.first_name}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('catalog:catalog')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('catalog:catalog')

def profile_view(request):
    """Vista de perfil de usuario"""
    return render(request, 'accounts/profile.html', {'user': request.user})

def profile_edit_view(request):
    """Vista para editar perfil"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

def verify_email(request, token):
    """Vista para verificar email con token"""
    try:
        user = User.objects.get(email_verification_token=token)
        
        # Verificar si el token no ha expirado (24 horas)
        if user.email_verification_sent_at:
            time_diff = timezone.now() - user.email_verification_sent_at
            if time_diff > timedelta(hours=24):
                messages.error(request, 'El link de verificación ha expirado. Solicita uno nuevo.')
                return redirect('accounts:resend_verification')
        
        if user.verify_email(token):
            messages.success(request, '¡Email verificado exitosamente! Ya puedes iniciar sesión.')
        else:
            messages.error(request, 'Token de verificación inválido.')
            
    except User.DoesNotExist:
        messages.error(request, 'Token de verificación inválido.')
    
    return redirect('accounts:login')

def resend_verification_email(request):
    """Vista para reenviar email de verificación"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_email_verified=False)
            send_verification_email(user, request)
            messages.success(request, 'Se ha enviado un nuevo link de verificación a tu correo.')
        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario no verificado con ese email.')
    
    return render(request, 'accounts/resend_verification.html')