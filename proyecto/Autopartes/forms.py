from django import forms
from .models import Usuarios, Productos, Ventas_detalles

class CrearUsuariosForm(forms.ModelForm):
    """
    Formulario para la creación de usuarios basado en el modelo Usuarios.
    """
    class Meta:
        model = Usuarios
        fields = ['nombre_usuario', 'email_usuario']
        labels = {
            'nombre_usuario': 'Nombre de Usuario',
            'email_usuario': 'Correo Electrónico',
        }
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            
            'email_usuario': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
        }


class CrearProductosForm(forms.ModelForm):
    """
    Formulario para la creación de productos basado en el modelo Productos.
    """
    class Meta:
        model = Productos
        fields = ['nombre_producto', 'marca_producto']
        labels = {
            'nombre_producto': 'Nombre del Producto',
            'marca_producto': 'Marca',
        }
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. Filtro de aceite'
            }),
            'marca_producto': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej. Bosch'
            }),
        }


class CrearVentasDetallesForm(forms.ModelForm):
    """
    Formulario para el registro de detalles de ventas con relación a Productos y Usuarios.
    """
    class Meta:
        model = Ventas_detalles
        fields = ['monto', 'fecha_venta', 'forma_de_pago', 'producto', 'usuario']
        labels = {
            'monto': 'Monto ($)',
            'fecha_venta': 'Fecha de Venta',
            'forma_de_pago': 'Forma de Pago',
            'producto': 'Producto Seleccionado',
            'usuario': 'Cliente/Usuario',
        }
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01'
            }),
            'fecha_venta': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'forma_de_pago': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Efectivo, Tarjeta, Transferencia'
            }),
            'producto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'usuario': forms.Select(attrs={
                'class': 'form-select'
            }),
        }