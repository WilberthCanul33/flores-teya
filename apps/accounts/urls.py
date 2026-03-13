from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.register_view, name='register'),
    path('iniciar-sesion/', views.login_view, name='login'),
    path('cerrar-sesion/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/editar/', views.profile_edit_view, name='profile_edit'),
    # NUEVAS URLs PARA VERIFICACIÓN
    path('verificar/<str:token>/', views.verify_email, name='verify_email'),
    path('reenviar-verificacion/', views.resend_verification_email, name='resend_verification'),
]