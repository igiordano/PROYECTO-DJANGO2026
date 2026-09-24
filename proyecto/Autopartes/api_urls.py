"""
Rutas de la API v1.

Se montan bajo `/api/v1/` desde `proyecto/urls.py`. La autenticacion usa JWT
(SimpleJWT): el cliente intercambia usuario y contrasena por un par de tokens
en `/api/v1/auth/token/` y renueva el token de acceso sin volver a pedir
credenciales.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import api_views

router = DefaultRouter()
router.register('productos', api_views.ProductoViewSet, basename='producto')
router.register('usuarios', api_views.UsuarioViewSet, basename='usuario')
router.register('ventas', api_views.VentaDetalleViewSet, basename='venta')
router.register(
    'mensajes-contacto',
    api_views.MensajeContactoViewSet,
    basename='mensaje-contacto',
)

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('reportes/ventas/', api_views.resumen_ventas, name='resumen-ventas'),
    path('', include(router.urls)),
]
