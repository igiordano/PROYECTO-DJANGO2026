from django.urls import path
from Autopartes import views

urlpatterns = [
    path('', views.mostrar_index, name='index'),
    path('productos/', views.mostrar_productos, name='productos'),    
    path('usuarios/', views.mostrar_usuarios, name='usuarios'),
    path('ventas-detalles/', views.mostrar_ventas_detalles, name='ventas_detalles'),
    path('crear_usuarios/', views.crear_usuario, name='Crear usuarios'),
    path('crear_productos/', views.crear_producto, name='Crear productos'),
    path('crear_ventas/', views.crear_ventas_detalles, name='Crear Ventas'),
    path('buscar-marca-producto/', views.buscar_marca_producto, name='buscar_marca_producto'),
    path('buscar-usuario/', views.buscar_usuario, name='buscar_usuario'),
    path('buscar-forma-de-pago/', views.buscar_forma_de_pago, name='buscar_forma_de_pago'),
    path('productos/actualizar/<int:productos_id>/', views.actualizar_producto, name='actualizar_producto'),
    path('productos/eliminar/<int:productos_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('usuarios/actualizar/<int:usuario_id>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('ventas/actualizar/<int:venta_id>/', views.actualizar_ventas_detalles, name='actualizar_ventas_detalles'),
    path('ventas/eliminar/<int:venta_id>/', views.eliminar_ventas_detalles, name='eliminar_ventas_detalles'),
    
]

