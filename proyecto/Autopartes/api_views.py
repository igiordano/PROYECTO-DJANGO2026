"""
Vistas de la API v1 (Django REST Framework).

Estrategia de permisos:
- El catalogo de productos es de lectura publica y de escritura autenticada,
  porque un cliente debe poder consultar repuestos sin registrarse.
- Usuarios y ventas quedan restringidos a cuentas de staff: contienen correos
  electronicos y montos, por lo que no pueden quedar anonimos como en el CRUD
  MVT actual.
- El formulario de contacto acepta envios anonimos, con limite de peticiones
  para evitar abuso.

Todas las vistas aplican paginacion, busqueda y ordenamiento para que la app
cliente nunca descargue tablas completas.
"""

from django.db.models import Avg, Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import MensajeContacto, Productos, Usuarios, Ventas_detalles
from .serializers import (
    MensajeContactoSerializer,
    ProductoSerializer,
    ResumenVentasSerializer,
    UsuarioSerializer,
    VentaDetalleSerializer,
)


class ProductoViewSet(viewsets.ModelViewSet):
    """CRUD del catalogo de autopartes.

    Filtros disponibles:
    - `?marca=bosch`: coincidencia parcial sobre la marca.
    - `?search=motor`: busqueda por nombre o marca (DjangoFilterBackend/search).
    - `?ordering=-nombre_producto`: orden por nombre o marca.
    """

    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre_producto', 'marca_producto']
    ordering_fields = ['nombre_producto', 'marca_producto', 'id']
    ordering = ['nombre_producto']

    def get_queryset(self):
        queryset = Productos.objects.all()
        marca = self.request.query_params.get('marca')
        if marca:
            queryset = queryset.filter(marca_producto__icontains=marca.strip())
        return queryset


class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios finales. Solo accesible para cuentas de staff."""

    queryset = Usuarios.objects.all().order_by('nombre_usuario')
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_usuario', 'email_usuario']
    ordering_fields = ['nombre_usuario', 'email_usuario', 'id']
    ordering = ['nombre_usuario']


class VentaDetalleViewSet(viewsets.ModelViewSet):
    """CRUD de ventas. Solo accesible para cuentas de staff.

    Filtros disponibles:
    - `?forma_de_pago=tarjeta`
    - `?producto=<id>` y `?usuario=<id>`
    - `?desde=2026-01-01&hasta=2026-12-31`
    """

    serializer_class = VentaDetalleSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'forma_de_pago',
        'producto__nombre_producto',
        'producto__marca_producto',
        'usuario__nombre_usuario',
        'usuario__email_usuario',
    ]
    ordering_fields = ['fecha_venta', 'monto', 'id']
    ordering = ['-fecha_venta', '-id']

    def get_queryset(self):
        queryset = Ventas_detalles.objects.select_related('producto', 'usuario')
        parametros = self.request.query_params
        forma_de_pago = parametros.get('forma_de_pago')
        if forma_de_pago:
            queryset = queryset.filter(
                forma_de_pago__icontains=forma_de_pago.strip()
            )
        producto = parametros.get('producto')
        if producto:
            queryset = queryset.filter(producto_id=producto)
        usuario = parametros.get('usuario')
        if usuario:
            queryset = queryset.filter(usuario_id=usuario)
        desde = parametros.get('desde')
        if desde:
            queryset = queryset.filter(fecha_venta__gte=desde)
        hasta = parametros.get('hasta')
        if hasta:
            queryset = queryset.filter(fecha_venta__lte=hasta)
        return queryset


class MensajeContactoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Alta de mensajes de contacto y listado para el equipo de soporte."""

    queryset = MensajeContacto.objects.all().order_by('-fecha_envio')
    serializer_class = MensajeContactoSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


@extend_schema(
    responses={200: ResumenVentasSerializer},
    description=(
        'Devuelve el total facturado, el ticket promedio y los cortes por forma '
        'de pago y por marca de producto. Requiere sesion de staff.'
    ),
)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def resumen_ventas(request):
    """Reporte agregado de ventas para el panel de la app cliente.

    Devuelve el total facturado, el ticket promedio y los cortes por forma de
    pago y por marca de producto.
    """
    agregados = Ventas_detalles.objects.aggregate(
        total=Coalesce(
            Sum('monto'),
            F('monto') * 0,
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ),
        cantidad=Count('id'),
        promedio=Avg('monto'),
    )

    por_forma_de_pago = list(
        Ventas_detalles.objects.values('forma_de_pago')
        .annotate(cantidad=Count('id'), monto=Sum('monto'))
        .order_by('-monto')
    )
    por_marca = list(
        Ventas_detalles.objects.values(marca=F('producto__marca_producto'))
        .annotate(cantidad=Count('id'), monto=Sum('monto'))
        .order_by('-monto')
    )

    datos = {
        'total_ventas': agregados['cantidad'],
        'monto_total': agregados['total'] or 0,
        'monto_promedio': round(agregados['promedio'] or 0, 2),
        'por_forma_de_pago': por_forma_de_pago,
        'por_marca': por_marca,
    }
    serializer = ResumenVentasSerializer(datos)
    return Response(serializer.data, status=status.HTTP_200_OK)
