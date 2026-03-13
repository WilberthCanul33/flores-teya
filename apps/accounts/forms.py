from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Formulario de registro personalizado - CORREGIDO"""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tus apellidos'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '555-123-4567'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado')
        return email
    
    def save(self, commit=True):
        """Guardar el usuario correctamente"""
        user = super().save(commit=False)
        user.username = user.email  # Usar email como username
        user.is_active = True
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Formulario de login personalizado"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña'
        })
    )
    
    def clean(self):
        """Autenticar usando email"""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,  # Django usa username, pero nosotros ponemos email
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Email o contraseña incorrectos',
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data

class UserProfileForm(forms.ModelForm):
    """Formulario para editar perfil"""
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'colonia', 'calle', 'numero_casa', 'entre_calles', 'referencias',
            'receive_offers'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '555-123-4567'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            'colonia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Centro'}),
            'calle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 60'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 123-A'}),
            'entre_calles': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 55 y 57'}),
            'referencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Frente al parque'}),
            
            'receive_offers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }