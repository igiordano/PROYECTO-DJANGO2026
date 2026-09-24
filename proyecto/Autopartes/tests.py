"""
Pruebas automatizadas del catalogo y de la API v1.

Cubren los huecos que la auditoria encontro en el proyecto original: no existia
ninguna prueba, el CRUD MVT no estaba protegido y faltaban validaciones de
negocio (montos negativos, fechas futuras, duplicados).

Ejecucion:
    python manage.py test
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Productos, Usuarios, Ventas_detalles


class BaseApiTest(TestCase):
    """Crea un usuario de staff y un cliente anonimo reutilizables."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='ClaveDePrueba123', is_staff=True
        )
        self.anon = APIClient()
        self.client_staff = APIClient()
        self.client_staff.force_authenticate(user=self.staff)


class ProductoApiTests(BaseApiTest):
    """El catalogo es publico para lectura y cerrado para escritura."""

    def setUp(self):
        super().setUp()
        self.producto = Productos.objects.create(
            nombre_producto='Filtro de aceite', marca_producto='Bosch'
        )

    def test_listado_publico_sin_autenticacion(self):
        respuesta = self.anon.get('/api/v1/productos/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['count'], 1)

    def test_creacion_anonima_rechazada(self):
        respuesta = self.anon.post(
            '/api/v1/productos/',
            {'nombre_producto': 'Bujia', 'marca_producto': 'NGK'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Productos.objects.count(), 1)

    def test_creacion_autenticada(self):
        respuesta = self.client_staff.post(
            '/api/v1/productos/',
            {'nombre_producto': 'Bujia iridio', 'marca_producto': 'NGK'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Productos.objects.count(), 2)

    def test_rechaza_producto_duplicado(self):
        respuesta = self.client_staff.post(
            '/api/v1/productos/',
            {'nombre_producto': 'filtro de aceite', 'marca_producto': 'BOSCH'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_busqueda_por_texto_libre(self):
        Productos.objects.create(
            nombre_producto='Disco de freno', marca_producto='Fiat'
        )
        respuesta = self.anon.get('/api/v1/productos/', {'search': 'fiat'})
        self.assertEqual(respuesta.data['count'], 1)

    def test_filtro_por_marca(self):
        Productos.objects.create(
            nombre_producto='Amortiguador', marca_producto='Fiat'
        )
        respuesta = self.anon.get('/api/v1/productos/', {'marca': 'bos'})
        self.assertEqual(respuesta.data['count'], 1)

    def test_eliminacion_anonima_rechazada(self):
        respuesta = self.anon.delete(f'/api/v1/productos/{self.producto.id}/')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Productos.objects.filter(id=self.producto.id).exists())


class UsuarioApiTests(BaseApiTest):
    """Los datos personales quedan reservados al staff."""

    def setUp(self):
        super().setUp()
        self.usuario = Usuarios.objects.create(
            nombre_usuario='pepe', email_usuario='pepe@ejemplo.com'
        )

    def test_listado_anonimo_rechazado(self):
        respuesta = self.anon.get('/api/v1/usuarios/')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listado_staff_permitido(self):
        respuesta = self.client_staff.get('/api/v1/usuarios/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['count'], 1)

    def test_email_duplicado_rechazado(self):
        respuesta = self.client_staff.post(
            '/api/v1/usuarios/',
            {'nombre_usuario': 'otro', 'email_usuario': 'PEPE@ejemplo.com'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_se_normaliza_a_minusculas(self):
        respuesta = self.client_staff.post(
            '/api/v1/usuarios/',
            {'nombre_usuario': 'nuevo', 'email_usuario': '  Nuevo@Ejemplo.COM '},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['email_usuario'], 'nuevo@ejemplo.com')


class VentaApiTests(BaseApiTest):
    """Validaciones de negocio sobre los detalles de venta."""

    def setUp(self):
        super().setUp()
        self.producto = Productos.objects.create(
            nombre_producto='Pastilla de freno', marca_producto='Bosch'
        )
        self.usuario = Usuarios.objects.create(
            nombre_usuario='pepe', email_usuario='pepe@ejemplo.com'
        )
        self.datos_validos = {
            'monto': '15000.50',
            'fecha_venta': timezone.localdate().isoformat(),
            'forma_de_pago': 'Tarjeta',
            'producto': self.producto.id,
            'usuario': self.usuario.id,
        }

    def test_creacion_valida(self):
        respuesta = self.client_staff.post(
            '/api/v1/ventas/', self.datos_validos, format='json'
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data['producto_nombre'], 'Pastilla de freno')
        self.assertEqual(respuesta.data['usuario_email'], 'pepe@ejemplo.com')

    def test_monto_negativo_rechazado(self):
        datos = {**self.datos_validos, 'monto': '-100'}
        respuesta = self.client_staff.post('/api/v1/ventas/', datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fecha_futura_rechazada(self):
        futura = (timezone.localdate() + timedelta(days=30)).isoformat()
        datos = {**self.datos_validos, 'fecha_venta': futura}
        respuesta = self.client_staff.post('/api/v1/ventas/', datos, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resumen_de_ventas(self):
        self.client_staff.post('/api/v1/ventas/', self.datos_validos, format='json')
        respuesta = self.client_staff.get('/api/v1/reportes/ventas/')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['total_ventas'], 1)
        self.assertEqual(
            respuesta.data['por_forma_de_pago'][0]['forma_de_pago'], 'Tarjeta'
        )
        self.assertEqual(respuesta.data['por_marca'][0]['marca'], 'Bosch')

    def test_resumen_anonimo_rechazado(self):
        respuesta = self.anon.get('/api/v1/reportes/ventas/')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)


class AutenticacionJwtTests(BaseApiTest):
    """El flujo de tokens es el que usara la app cliente."""

    def test_obtener_y_usar_token(self):
        respuesta = self.anon.post(
            '/api/v1/auth/token/',
            {'username': 'staff', 'password': 'ClaveDePrueba123'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        access = respuesta.data['access']
        self.assertIn('refresh', respuesta.data)

        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        self.assertEqual(
            cliente.get('/api/v1/usuarios/').status_code, status.HTTP_200_OK
        )

    def test_token_invalido_rechazado(self):
        respuesta = self.anon.post(
            '/api/v1/auth/token/',
            {'username': 'staff', 'password': 'incorrecta'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)


class ContactoApiTests(BaseApiTest):
    """El formulario de contacto es publico pero limitado."""

    def test_envio_anonimo_permitido(self):
        respuesta = self.anon.post(
            '/api/v1/mensajes-contacto/',
            {
                'nombre': 'Ana',
                'email': 'ana@ejemplo.com',
                'mensaje': 'Necesito un presupuesto por un radiador.',
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_listado_anonimo_rechazado(self):
        respuesta = self.anon.get('/api/v1/mensajes-contacto/')
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
