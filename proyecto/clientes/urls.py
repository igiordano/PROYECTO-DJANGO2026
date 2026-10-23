from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('panel/', views.panel_cliente, name='panel_cliente'),
    path('login-cliente/', views.login_cliente, name='login_cliente'),
    path('logout/', views.logout_cliente, name='logout_cliente'),
    path('registro/', views.registro_cliente, name='registro_cliente'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('quitar/<int:item_id>/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    path("perfil-cliente/", views.perfil_cliente, name="perfil_cliente"),

]