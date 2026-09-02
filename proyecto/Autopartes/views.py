from django.shortcuts import render
from Autopartes.models import *
# Create your views here.

def mostrar_index(request):


    return render(request, 'Autopartes/index.html')

def mostrar_productos(request):

    producto = Productos.objects.all()

    context = {'producto': producto}

    return render(request, 'Autopartes/productos.html', context=context)

def mostrar_usuarios(request):

    usuario = Usuarios.objects.all()

    context = {'usuario':  usuario}

    return render(request, 'Autopartes/usuarios.html', context=context)

def mostrar_ventas_detalles(request):

    venta_detalle = Ventas_detalles.objects.all()

    context = {'venta_detalle':  venta_detalle}

    return render(request, 'Autopartes/ventas_detalles.html', context=context)


