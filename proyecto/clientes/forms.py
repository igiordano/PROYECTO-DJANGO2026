# clientes/forms.py
# Este archivo define los formularios del módulo de clientes.
# Cada formulario se conecta con un modelo de Django y permite validar la información
# antes de guardarla en la base de datos.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput
from .models import Cliente


class UserRegistrationForm(UserCreationForm):
    """
    Formulario para registrar un nuevo usuario desde la parte cliente.
    Hereda de UserCreationForm para reutilizar la lógica de creación de usuarios
    de Django y agrega campos personalizados para la información básica.
    """
    # Campo para el nombre de usuario que se mostrará en el formulario.
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    # Correo electrónico obligatorio del usuario.
    email = forms.EmailField(label="Correo electrónico")
    # Contraseña con entrada ocultada para que no se vea al escribir.
    password1 = forms.CharField(widget=PasswordInput, label="Contraseña")
    # Confirmación de la contraseña para validar que ambas coinciden.
    password2 = forms.CharField(widget=PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = User
        # Campos que se renderizan en el formulario y se guardan en el modelo User.
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        """
        Valida que las dos contraseñas ingresadas coincidan antes de guardar.
        Si no coinciden, agrega un error visual al campo de confirmación.
        """
        cleaned_data = super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')

        return cleaned_data


class UsuarioForm(forms.ModelForm):
    """
    Formulario para editar la información personal del usuario autenticado.
    Se usa para actualizar nombre, apellido y correo desde el perfil del cliente.
    """
    class Meta:
        model = User
        # Campos del modelo User que se pueden modificar desde este formulario.
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }
        widgets = {
            # La clase CSS ayuda a mantener un estilo visual consistente en la interfaz.
            'first_name': forms.TextInput(attrs={'class': 'form-control-input', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control-input', 'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-input', 'placeholder': 'ejemplo@correo.com'}),
        }


class PerfilClienteForm(forms.ModelForm):
    """
    Formulario para completar los datos del perfil de un cliente.
    Se usa para guardar información adicional como teléfono, dirección y ciudad.
    """
    class Meta:
        model = Cliente
        # Campos del modelo Cliente que se pueden editar desde el perfil.
        fields = ['telefono', 'direccion', 'ciudad']
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
        }
        widgets = {
            # Los placeholders guían al usuario sobre el formato esperado.
            'telefono': forms.TextInput(attrs={'class': 'form-control-input', 'placeholder': 'Tu teléfono'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control-input', 'placeholder': 'Tu dirección'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control-input', 'placeholder': 'Tu ciudad'}),
        }