from django.urls import path
from Autopartes import views

urlpatterns = [
    path('', views.mostrar_index, name='index'),
    path('productos/', views.mostrar_productos, name='productos'),    
    path('usuarios/', views.mostrar_usuarios, name='usuarios'),
    path('ventas-detalles/', views.mostrar_ventas_detalles, name='ventas_detalles'),
]

