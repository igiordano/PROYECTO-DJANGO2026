"""
Serializers de la API v1.

Expone los modelos existentes (Usuarios, Productos, Ventas_detalles y
MensajeContacto) agregando las validaciones que los formularios MVT no
aplicaban: texto normalizado, unicidad de nombre+marca, montos positivos y
fechas de venta no futuras.

Los formularios MVT originales permanecen intactos: este módulo solo se usa
desde la API.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import MensajeContacto, Productos, Usuarios, Ventas_detalles


class ProductoSerializer(serializers.ModelSerializer):
    """Producto del catalogo de autopartes."""

    class Meta:
        model = Productos
        fields = ['id', 'nombre_producto', 'marca_producto']
        read_only_fields = ['id']

    def validate_nombre_producto(self, value):
        value = ' '.join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError(
                'El nombre del producto debe tener al menos 2 caracteres.'
            )
        return value

    def validate_marca_producto(self, value):
        value = ' '.join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError(
                'La marca debe tener al menos 2 caracteres.'
            )
        return value

    def validate(self, attrs):
        """Evita cargar dos veces el mismo par nombre + marca.

        Es una verificacion a nivel de aplicacion porque el modelo todavia no
        declara una restriccion `UniqueConstraint` en la base de datos.
        """
        nombre = attrs.get(
            'nombre_producto', getattr(self.instance, 'nombre_producto', None)
        )
        marca = attrs.get(
            'marca_producto', getattr(self.instance, 'marca_producto', None)
        )
        duplicados = Productos.objects.filter(
            nombre_producto__iexact=nombre, marca_producto__iexact=marca
        )
        if self.instance is not None:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise serializers.ValidationError(
                f'Ya existe el producto "{nombre}" de la marca "{marca}".'
            )
        return attrs


class UsuarioSerializer(serializers.ModelSerializer):
    """Cliente o usuario final asociado a las ventas."""

    class Meta:
        model = Usuarios
        fields = ['id', 'nombre_usuario', 'email_usuario']
        read_only_fields = ['id']

    def validate_nombre_usuario(self, value):
        value = ' '.join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError(
                'El nombre de usuario debe tener al menos 2 caracteres.'
            )
        return value

    def validate_email_usuario(self, value):
        email = value.strip().lower()
        duplicados = Usuarios.objects.filter(email_usuario__iexact=email)
        if self.instance is not None:
            duplicados = duplicados.exclude(pk=self.instance.pk)
        if duplicados.exists():
            raise serializers.ValidationError(
                'Ya existe un usuario registrado con ese correo electronico.'
            )
        return email


class VentaDetalleSerializer(serializers.ModelSerializer):
    """Detalle de venta con los datos relacionados listos para mostrar.

    Los campos `producto_nombre`, `producto_marca`, `usuario_nombre` y
    `usuario_email` son de solo lectura y existen para que la app cliente no
    tenga que resolver las claves foraneas con llamadas adicionales.
    """

    producto_nombre = serializers.CharField(
        source='producto.nombre_producto', read_only=True
    )
    producto_marca = serializers.CharField(
        source='producto.marca_producto', read_only=True
    )
    usuario_nombre = serializers.CharField(
        source='usuario.nombre_usuario', read_only=True
    )
    usuario_email = serializers.EmailField(
        source='usuario.email_usuario', read_only=True
    )

    class Meta:
        model = Ventas_detalles
        fields = [
            'id',
            'monto',
            'fecha_venta',
            'forma_de_pago',
            'producto',
            'usuario',
            'producto_nombre',
            'producto_marca',
            'usuario_nombre',
            'usuario_email',
        ]
        read_only_fields = ['id']

    def validate_monto(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('El monto debe ser mayor a cero.')
        return value

    def validate_fecha_venta(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                'La fecha de venta no puede ser futura.'
            )
        return value

    def validate_forma_de_pago(self, value):
        value = ' '.join(value.split())
        if len(value) < 3:
            raise serializers.ValidationError(
                'Indique una forma de pago valida (Ej. Efectivo, Tarjeta).'
            )
        return value


class MensajeContactoSerializer(serializers.ModelSerializer):
    """Mensaje enviado desde el formulario de contacto publico."""

    class Meta:
        model = MensajeContacto
        fields = ['id', 'nombre', 'email', 'mensaje', 'fecha_envio']
        read_only_fields = ['id', 'fecha_envio']


class ResumenVentasSerializer(serializers.Serializer):
    """Estructura de salida del reporte agregado de ventas."""

    total_ventas = serializers.IntegerField()
    monto_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    monto_promedio = serializers.DecimalField(max_digits=14, decimal_places=2)
    por_forma_de_pago = serializers.ListField(child=serializers.DictField())
    por_marca = serializers.ListField(child=serializers.DictField())
