from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from Autopartes.models import Productos, Ventas_detalles
from .forms import PerfilClienteForm, UserRegistrationForm
from .models import Carrito, Cliente, DetallePedido, Pedido


def _obtener_o_crear_cliente(user):
    """
    Garantiza que el usuario autenticado tenga un perfil Cliente asociado.
    """
    cliente, _ = Cliente.objects.get_or_create(usuario=user)
    return cliente


def login_cliente(request):
    """Valida las credenciales e inicia sesión solo para cuentas de cliente."""
    if request.method == 'POST':
        # En POST se validan las credenciales recibidas desde el formulario.
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            if not usuario.is_staff:
                # Las cuentas del panel administrativo deben usar su acceso propio.
                login(request, usuario)
                messages.success(request, 'Sesión de cliente iniciada.')
                return redirect('panel_cliente')
            form.add_error(None, 'Usa el acceso de administrador para usuarios del panel.')
    else:
        form = AuthenticationForm()

    return render(request, 'clientes/login_cliente.html', {'form': form})


@login_required
def panel_cliente(request):
    """Muestra el panel personal; requiere que el cliente haya iniciado sesión."""
    return render(request, 'clientes/panel_cliente.html')


def catalogo(request):
    """Obtiene todos los productos y los muestra en el catálogo público."""
    productos = Productos.objects.all()
    return render(request, 'clientes/catalogo.html', {'productos': productos})


def registro_cliente(request):
    """Registra una cuenta de cliente, crea su perfil y deja la sesión iniciada."""
    if request.method == 'POST':
        # Procesa los datos enviados y solo crea la cuenta si el formulario es válido.
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # La cuenta y su perfil se guardan juntos para evitar registros incompletos.
            with transaction.atomic():
                user = form.save()
                Cliente.objects.create(usuario=user)
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido/a.')
            return redirect('panel_cliente')
    else:
        form = UserRegistrationForm()

    return render(request, 'clientes/registro.html', {'form': form})


@login_required
def detalle_producto(request, producto_id):
    """Busca un producto por ID y presenta su información detallada."""
    producto = get_object_or_404(Productos, id=producto_id)
    return render(request, 'clientes/detalle.html', {'producto': producto})


@login_required
@require_POST
def agregar_al_carrito(request, producto_id):
    """
    Agrega una unidad al carrito si hay existencias; solo acepta solicitudes POST.
    """
    # Si el ID no existe, Django responde con una página 404.
    producto = get_object_or_404(Productos, id=producto_id)
    cliente = _obtener_o_crear_cliente(request.user)

    # Reutiliza la línea existente del carrito o crea una con cantidad inicial.
    item, created = Carrito.objects.get_or_create(cliente=cliente, producto=producto)

    # Validamos existencias de stock antes de incrementar la cantidad
    if not created:
        if item.cantidad + 1 > producto.stock:
            messages.warning(request, f'No hay suficiente stock disponible para "{producto.nombre_producto}".')
            return redirect('catalogo')
        item.cantidad += 1
        item.save()
    else:
        if producto.stock < 1:
            messages.warning(request, f'El producto "{producto.nombre_producto}" se encuentra agotado.')
            item.delete()
            return redirect('catalogo')

    messages.success(request, f'Se agregó "{producto.nombre_producto}" al carrito.')
    return redirect('catalogo')


@login_required
def carrito(request):
    """Lista los artículos del cliente autenticado y calcula el total actual."""
    cliente = _obtener_o_crear_cliente(request.user)
    items = Carrito.objects.filter(cliente=cliente)
    total = sum(item.subtotal() for item in items)
    return render(request, 'clientes/carrito.html', {'items': items, 'total': total})


@login_required
@require_POST
def quitar_del_carrito(request, item_id):
    """Elimina del carrito un artículo que pertenezca al cliente autenticado."""
    cliente = _obtener_o_crear_cliente(request.user)
    # La búsqueda también comprueba la propiedad para impedir borrar carritos ajenos.
    item = get_object_or_404(Carrito, id=item_id, cliente=cliente)
    item.delete()
    messages.info(request, 'Producto eliminado del carrito.')
    return redirect('carrito')


@login_required
def checkout(request):
    """Confirma la compra, registra el pedido y descuenta las existencias."""
    cliente = _obtener_o_crear_cliente(request.user)
    items = Carrito.objects.filter(cliente=cliente)

    # No se permite iniciar el pago si no hay artículos para comprar.
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito')

    if request.method == 'POST':
        # Pedido, detalles, inventario y carrito se actualizan en una sola transacción.
        with transaction.atomic():
            # 1. Comprobar que cada producto tenga stock suficiente
            for item in items:
                if item.cantidad > item.producto.stock:
                    messages.error(
                        request,
                        f'El producto "{item.producto.nombre_producto}" supera el stock disponible ({item.producto.stock} unidades).'
                    )
                    return redirect('carrito')

            total = sum(item.subtotal() for item in items)

            # 2. Registrar la orden de pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                total=total,
                metodo_pago=request.POST.get('metodo_pago', 'efectivo')
            )

            # 3. Guardar el pedido, generar sus ventas y descontar el inventario.
            for item in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
                Ventas_detalles.objects.create(
                    monto=float(item.subtotal()),
                    fecha_venta=timezone.localdate(),
                    forma_de_pago=pedido.metodo_pago,
                    producto=item.producto,
                    cliente=cliente,
                    pedido=pedido,
                )

                # Restamos las unidades compradas del stock en Autopartes
                item.producto.stock -= item.cantidad
                item.producto.save()

            # 4. Vaciar el carrito de la sesión
            items.delete()

        messages.success(request, '¡Compra realizada con éxito!')
        return redirect('mis_pedidos')

    total = sum(item.subtotal() for item in items)
    return render(request, 'clientes/checkout.html', {'items': items, 'total': total})


@login_required
def mis_pedidos(request):
    """Muestra los pedidos del cliente, del más reciente al más antiguo."""
    cliente = _obtener_o_crear_cliente(request.user)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha')
    return render(request, 'clientes/pedidos.html', {'pedidos': pedidos})


@login_required
@require_POST
def confirmar_pedido(request, pedido_id):
    """Marca como pagado un pedido pendiente del cliente autenticado."""
    cliente = _obtener_o_crear_cliente(request.user)
    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(), id=pedido_id, cliente=cliente
        )
        if pedido.estado != 'pendiente':
            messages.warning(request, 'Solo puedes confirmar pedidos pendientes.')
            return redirect('mis_pedidos')

        pedido.estado = 'pagado'
        pedido.save(update_fields=['estado'])

    messages.success(request, f'El pedido #{pedido.id} fue confirmado.')
    return redirect('mis_pedidos')


@login_required
@require_POST
def cancelar_pedido(request, pedido_id):
    """Cancela un pedido pendiente y devuelve sus unidades al inventario."""
    cliente = _obtener_o_crear_cliente(request.user)
    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(), id=pedido_id, cliente=cliente
        )
        if pedido.estado != 'pendiente':
            messages.warning(request, 'Solo puedes cancelar pedidos pendientes.')
            return redirect('mis_pedidos')

        # La actualización atómica evita sobrescribir cambios concurrentes de stock.
        for detalle in DetallePedido.objects.filter(pedido=pedido):
            Productos.objects.filter(id=detalle.producto_id).update(
                stock=F('stock') + detalle.cantidad
            )

        Ventas_detalles.objects.filter(pedido=pedido).delete()
        pedido.estado = 'cancelado'
        pedido.save(update_fields=['estado'])

    messages.success(request, f'El pedido #{pedido.id} fue cancelado.')
    return redirect('mis_pedidos')


@login_required
def perfil(request):
    """Muestra y actualiza el perfil del cliente mediante un formulario Django."""
    cliente = _obtener_o_crear_cliente(request.user)
    if request.method == 'POST':
        # El formulario carga los datos existentes y valida los cambios enviados.
        form = PerfilClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        # En GET, el formulario se presenta con los datos actuales del perfil.
        form = PerfilClienteForm(instance=cliente)

    return render(request, 'clientes/perfil.html', {'form': form})

from .forms import UsuarioForm, PerfilClienteForm

# clientes/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente

@login_required
def perfil_cliente(request):
    """
    Vista que recupera y actualiza los datos del cliente logueado
    procesando directamente las peticiones HTTP POST.
    """
    """Actualiza manualmente los datos personales y de contacto del cliente."""
    # Garantiza que exista un perfil asociado al usuario que inició sesión.
    cliente, created = Cliente.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        # Lee los campos del formulario y elimina espacios sobrantes al inicio/final.
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()

        # Nombre y correo pertenecen al usuario de autenticación de Django.
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Teléfono y dirección pertenecen al perfil Cliente.
        cliente.telefono = telefono
        cliente.direccion = direccion
        cliente.ciudad = ciudad
        cliente.save()

        messages.success(request, '¡Tus datos se actualizaron correctamente!')
        return redirect('perfil_cliente')

    # En GET se envían los datos actuales a la plantilla para rellenar el formulario.
    context = {
        'cliente': cliente
    }
    return render(request, 'clientes/perfil.html', context)

def logout_cliente(request):
    """Cierra la sesión actual y vuelve a la página principal con un mensaje."""
    logout(request)
    return render(request, "Autopartes/index.html", {"mensaje": "Has cerrado sesión exitosamente."})