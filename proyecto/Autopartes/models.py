from django.db import models
from django.utils import timezone


class Usuarios(models.Model):
    """Registro basico de nombre y correo usado por las funciones administrativas antiguas."""

    # Nombre y correo de este registro independiente del usuario de autenticacion de Django.
    nombre_usuario = models.CharField(max_length=30)
    email_usuario = models.EmailField()

    def __str__(self):
        """Devuelve el nombre y el correo para identificar el registro en Django."""
        return f'Nombre_usuario: {self.nombre_usuario}, Email_usuario: {self.email_usuario}'


class Productos(models.Model):
    """Producto del catalogo con precio y existencias disponibles."""

    # Datos que identifican el producto y su marca.
    nombre_producto = models.CharField(max_length=30)
    marca_producto = models.CharField(max_length=20)
    # Precio unitario y unidades disponibles para la venta.
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)

    def __str__(self):
        """Muestra el nombre, la marca y el precio del producto."""
        return f'{self.nombre_producto} ({self.marca_producto}) - ${self.precio}'


class Ventas_detalles(models.Model):
    """Linea de venta que asocia un producto con el cliente y, opcionalmente, su pedido."""

    # Importe de esta linea de venta y fecha en que se registro.
    monto = models.FloatField()
    fecha_venta = models.DateField()
    # Metodo utilizado para pagar esta venta.
    forma_de_pago = models.CharField(max_length=25)
    # Eliminar el producto o cliente elimina tambien la linea relacionada.
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    # Puede estar vacio para ventas manuales; si se borra el pedido, la venta se conserva.
    pedido = models.ForeignKey(
        'clientes.Pedido', null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        """Resume el importe, fecha, pago, producto y cliente de la venta."""
        return f'Monto: {self.monto}, Fecha_venta: {self.fecha_venta}, Forma_de_pago: {self.forma_de_pago}, producto: {self.producto}, cliente: {self.cliente}'


class MensajeContacto(models.Model):
    """Mensaje enviado al negocio desde el formulario de contacto."""

    # Datos de contacto y contenido proporcionados por quien envia el mensaje.
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    # Se establece automaticamente al crear el registro.
    fecha_envio = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Identifica el mensaje por el nombre y correo de quien lo envio."""
        return f'Mensaje de {self.nombre} - {self.email}'

