"""
URLs raiz del proyecto.

Orden de resolucion:
1. `/admin/` para la administracion de Django.
2. `/api/v1/` para la API REST que consume la app cliente.
3. `/api/docs/` y `/api/redoc/` para la documentacion interactiva (OpenAPI).
4. Las vistas MVT originales, montadas en la raiz y resueltas al final.

La inclusion de `Autopartes.urls` queda ultima para que no capture las rutas de
la API. La version original usaba `re_path('', include(...))`, que se comporta
como un comodin; `path` es suficiente y mas explicito.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('Autopartes.api_urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
    path('', include('Autopartes.urls')),
]
