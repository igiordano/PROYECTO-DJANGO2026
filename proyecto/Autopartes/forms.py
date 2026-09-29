from django import forms
from .models import Usuarios, Productos, Ventas_detalles


# Este formulario se usa para crear nuevos registros en el modelo Usuarios.
# Sirve para guardar el nombre de usuario y su correo electrónico desde la vista
# de administración o gestión del sistema.
class CrearUsuariosForm(forms.ModelForm):
    """
    Formulario para la creación de usuarios basado en el modelo Usuarios.
    """
    class Meta:
        model = Usuarios
        # Campos del modelo que se mostrarán en el formulario.
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


# Este formulario permite registrar un producto con sus datos básicos.
# Incluye nombre, marca, precio y cantidad disponible para controlar el inventario.
class CrearProductosForm(forms.ModelForm):
    """
    Formulario para la creación de productos basado en el modelo Productos.
    Incluye los campos de precio y stock.
    """
    class Meta:
        model = Productos
        # Se muestran los datos del producto que son relevantes para la venta y el stock.
        fields = ['nombre_producto', 'marca_producto', 'precio', 'stock']
        labels = {
            'nombre_producto': 'Nombre del Producto',
            'marca_producto': 'Marca',
            'precio': 'Precio ($)',
            'stock': 'Stock Disponible',
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
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
        }


# Este formulario registra los detalles de una venta vinculada a un producto y a un cliente.
# Permite guardar el monto, la fecha, la forma de pago y las relaciones con otros modelos.
class CrearVentasDetallesForm(forms.ModelForm):
    """
    Formulario para el registro de detalles de ventas con relación a Productos y Clientes.
    """
    class Meta:
        model = Ventas_detalles
        # Aquí se incluyen los campos necesarios para registrar una venta y relacionarla
        # con el producto vendido y el cliente que realizó la compra.
        fields = ['monto', 'fecha_venta', 'forma_de_pago', 'producto', 'cliente']
        labels = {
            'monto': 'Monto ($)',
            'fecha_venta': 'Fecha de Venta',
            'forma_de_pago': 'Forma de Pago',
            'producto': 'Producto Seleccionado',
            'cliente': 'Cliente',
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
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
        }