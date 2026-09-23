from django.shortcuts import render, redirect, get_object_or_404
from Autopartes.models import *
from django.contrib import messages
from .forms import CrearUsuariosForm, CrearProductosForm, CrearVentasDetallesForm
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

def crear_producto(request):
    """
    Vista para procesar la creación de un nuevo Producto.
    """
    if request.method == 'POST':
        # Instanciamos el formulario con los datos enviados en la petición POST
        form = CrearProductosForm(request.POST)
        
        if form.is_valid():
            # Al usar ModelForm, .save() crea y guarda la instancia directamente en la BD
            producto_creado = form.save()
            
            # Notificamos al usuario del éxito de la operación
            messages.success(request, f'Producto "{producto_creado.nombre_producto}" creado con éxito.')
            
            # Redirigimos a la página principal para evitar reenvíos de formulario
            return redirect('productos') 
    else:
        # Petición GET: creamos una instancia vacía del formulario
        form = CrearProductosForm()

    # Renderizamos la plantilla pasando el formulario como contexto
    return render(request, 'Autopartes/crear_productos.html', {'form': form})


def crear_usuario(request):
    """
    Vista para procesar el registro de un nuevo Usuario.
    """
    if request.method == 'POST':
        form = CrearUsuariosForm(request.POST)
        
        if form.is_valid():
            usuario_creado = form.save()
            
            messages.success(request, f'Usuario "{usuario_creado.nombre_usuario}" registrado con éxito.')
            
            return redirect('usuarios')
    else:
        form = CrearUsuariosForm()

    return render(request, 'Autopartes/crear_usuarios.html', {'form': form})


def crear_ventas_detalles(request):
    """
    Vista para registrar un nuevo detalle de venta asociando Producto y Usuario.
    """
    if request.method == 'POST':
        form = CrearVentasDetallesForm(request.POST)
        
        if form.is_valid():
            venta_creada = form.save()
            
            messages.success(request, 'Detalle de venta registrado correctamente.')
            
            return redirect('ventas_detalles')
    else:
        form = CrearVentasDetallesForm()

    return render(request, 'Autopartes/crear_ventas.html', {'form': form})


def buscar_marca_producto(request):
    """
    Vista para buscar productos por su marca mediante el parametro GET 'marca_producto'.
    """
    # Obtiene el valor del parametro 'marca_producto', o una cadena vacia si no existe
    marca_producto = request.GET.get('marca_producto', '').strip()
    
    contexto = {}

    if marca_producto:
        # Realiza la busqueda insensible a mayusculas/minusculas
        productos_encontrados = Productos.objects.filter(marca_producto__icontains=marca_producto)
        
        contexto['productos'] = productos_encontrados
        contexto['termino_busqueda'] = marca_producto
        
        if not productos_encontrados.exists():
            contexto['respuesta'] = f'No se encontraron productos para la marca "{marca_producto}".'
    else:
        contexto['respuesta'] = 'Ingrese una marca para realizar la búsqueda.'

    return render(request, 'Autopartes/buscar_marca_producto.html', contexto)


def buscar_usuario(request):
    """
    Vista para buscar usuarios por su correo electronico mediante el parametro GET 'email_usuario'.
    """
    email = request.GET.get('email_usuario', '').strip()
    
    contexto = {}

    if email:
        usuarios_encontrados = Usuarios.objects.filter(email_usuario__icontains=email)
        
        contexto['usuarios'] = usuarios_encontrados
        contexto['termino_busqueda'] = email
        
        if not usuarios_encontrados.exists():
            contexto['respuesta'] = f'No se encontraron usuarios con el correo "{email}".'
    else:
        contexto['respuesta'] = 'Ingrese un correo electrónico para realizar la búsqueda.'

    return render(request, 'Autopartes/buscar_usuarios.html', contexto)


def buscar_forma_de_pago(request):
    """
    Vista para buscar detalles de ventas por forma de pago mediante el parametro GET 'forma_de_pago'.
    """
    forma_de_pago = request.GET.get('forma_de_pago', '').strip()
    
    contexto = {}

    if forma_de_pago:
        ventas_encontradas = Ventas_detalles.objects.filter(forma_de_pago__icontains=forma_de_pago)
        
        contexto['ventas_detalles'] = ventas_encontradas
        contexto['termino_busqueda'] = forma_de_pago
        
        if not ventas_encontradas.exists():
            contexto['respuesta'] = f'No se registraron ventas con la forma de pago "{forma_de_pago}".'
    else:
        contexto['respuesta'] = 'Ingrese una forma de pago para realizar la búsqueda.'

    return render(request, 'Autopartes/buscar_ventas_detalles.html', contexto)



# ==========================================
# VISTAS DE ACTUALIZACIÓN (UPDATE)
# ==========================================

def actualizar_producto(request, productos_id):
    """
    Carga y actualiza los datos de un producto existente.
    """
    producto = get_object_or_404(Productos, id=productos_id)
    
    if request.method == 'POST':
        form = CrearProductosForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" actualizado correctamente.')
            return redirect('productos')
    else:
        form = CrearProductosForm(instance=producto)

    return render(request, 'Autopartes/actualizar_producto.html', {'form': form, 'producto': producto})


def actualizar_usuario(request, usuario_id):
    """
    Carga y actualiza los datos de un usuario existente.
    """
    usuario = get_object_or_404(Usuarios, id=usuario_id)
    
    if request.method == 'POST':
        form = CrearUsuariosForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.nombre_usuario}" actualizado correctamente.')
            return redirect('usuarios')
    else:
        form = CrearUsuariosForm(instance=usuario)

    return render(request, 'Autopartes/actualizar_usuario.html', {'form': form, 'usuario': usuario})


def actualizar_ventas_detalles(request, venta_id):
    """
    Carga y actualiza los datos de un detalle de venta existente.
    """
    venta_detalle = get_object_or_404(Ventas_detalles, id=venta_id)
    
    if request.method == 'POST':
        form = CrearVentasDetallesForm(request.POST, instance=venta_detalle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Detalle de venta actualizado correctamente.')
            return redirect('ventas_detalles')
    else:
        form = CrearVentasDetallesForm(instance=venta_detalle)

    return render(request, 'Autopartes/actualizar_ventas_detalles.html', {'form': form, 'venta_detalle': venta_detalle})

# ==========================================
# VISTAS DE ELIMINACIÓN (DELETE)
# ==========================================

def eliminar_producto(request, productos_id):
    """
    Vista para confirmar y procesar la eliminación de un producto.
    """
    # 1. Buscamos el producto por su ID o devolvemos un error 404 si no existe
    producto = get_object_or_404(Productos, id=productos_id)
    
    # 2. Si la petición es POST (el usuario hizo clic en "Sí, Eliminar" dentro del HTML de advertencia)
    if request.method == 'POST':
        nombre = producto.nombre_producto
        producto.delete()  # Se borra el registro en la base de datos
        
        # Enviamos un mensaje de notificación y redirigimos al listado
        messages.warning(request, f'Producto "{nombre}" eliminado correctamente.')
        return redirect('productos')
        
    # 3. Si la petición es GET (el usuario solo hizo clic en "Eliminar" desde la tabla),
    # simplemente mostramos la pantalla de confirmación/advertencia.
    return render(request, 'Autopartes/eliminar_producto.html', {'producto': producto})


def eliminar_usuario(request, usuario_id):
    """
    Vista para confirmar y procesar la eliminación de un usuario.
    """
    # 1. Buscamos el usuario por su ID o devolvemos un error 404 si no existe
    usuario = get_object_or_404(Usuarios, id=usuario_id)
    
    # 2. Si el usuario confirma la eliminación enviando el formulario (método POST)
    if request.method == 'POST':
        nombre = usuario.nombre_usuario
        usuario.delete()  # Se elimina el registro de la base de datos
        
        messages.warning(request, f'Usuario "{nombre}" eliminado correctamente.')
        return redirect('usuarios')
    
    # 3. Si es una petición GET, renderizamos la pantalla de advertencia
    return render(request, 'Autopartes/eliminar_usuario.html', {'usuario': usuario})


def eliminar_ventas_detalles(request, venta_id):
    """
    Vista para confirmar y procesar la eliminación de un detalle de venta.
    """
    # 1. Buscamos la venta por su ID o devolvemos un error 404 si no existe
    venta_detalle = get_object_or_404(Ventas_detalles, id=venta_id)
    
    # 2. Si se confirma la eliminación enviando el formulario (método POST)
    if request.method == 'POST':
        venta_detalle.delete()  # Se elimina el registro de la base de datos
        
        messages.warning(request, 'Detalle de venta eliminado correctamente.')
        return redirect('ventas_detalles')
    
    # 3. Si es una petición GET, renderizamos la pantalla de advertencia
    return render(request, 'Autopartes/eliminar_ventas_detalles.html', {'venta_detalle': venta_detalle})
