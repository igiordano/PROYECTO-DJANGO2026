from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from Autopartes.models import Productos, Ventas_detalles

from .models import Cliente, DetallePedido, Pedido


class RegistroClienteTests(TestCase):
	def test_muestra_formulario_de_registro(self):
		response = self.client.get(reverse('registro_cliente'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Registro de Cliente')
		self.assertContains(response, 'Registrarse')

	def test_registro_crea_usuario_y_cliente_e_inicia_sesion(self):
		response = self.client.post(
			reverse('registro_cliente'),
			{
				'username': 'cliente_nuevo',
				'email': 'cliente@example.com',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
			},
		)

		self.assertRedirects(response, reverse('panel_cliente'))
		user = User.objects.get(username='cliente_nuevo')
		self.assertTrue(Cliente.objects.filter(usuario=user).exists())
		self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

	def test_passwords_distintas_no_crean_cuenta(self):
		response = self.client.post(
			reverse('registro_cliente'),
			{
				'username': 'cliente_invalido',
				'email': 'cliente@example.com',
				'password1': 'ClaveSegura123!',
				'password2': 'OtraClave123!',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(User.objects.filter(username='cliente_invalido').exists())
		self.assertContains(response, 'Las contraseñas no coinciden')


class LoginClienteTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='cliente_login',
			password='ClaveSegura123!',
		)
		Cliente.objects.create(usuario=self.user)

	def test_login_cliente_redirige_al_panel(self):
		response = self.client.post(
			reverse('login_cliente'),
			{'username': 'cliente_login', 'password': 'ClaveSegura123!'},
		)

		self.assertRedirects(response, reverse('panel_cliente'))
		self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

	def test_usuario_administrador_no_puede_entrar_como_cliente(self):
		self.user.is_staff = True
		self.user.save(update_fields=['is_staff'])

		response = self.client.post(
			reverse('login_cliente'),
			{'username': 'cliente_login', 'password': 'ClaveSegura123!'},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Usa el acceso de administrador')


class AccionesPedidoTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='cliente_pedidos',
			password='ClaveSegura123!',
		)
		self.cliente = Cliente.objects.create(usuario=self.user)
		self.producto = Productos.objects.create(
			nombre_producto='Filtro', marca_producto='Auto', precio='10.00', stock=3,
		)
		self.pedido = Pedido.objects.create(cliente=self.cliente, total='20.00')
		DetallePedido.objects.create(
			pedido=self.pedido,
			producto=self.producto,
			cantidad=2,
			precio_unitario='10.00',
		)
		Ventas_detalles.objects.create(
			monto=20,
			fecha_venta='2026-09-28',
			forma_de_pago='efectivo',
			producto=self.producto,
			cliente=self.cliente,
			pedido=self.pedido,
		)
		self.client.force_login(self.user)

	def test_confirmar_pedido_cambia_estado_a_pagado(self):
		response = self.client.post(
			reverse('confirmar_pedido', args=[self.pedido.id]),
		)

		self.assertRedirects(response, reverse('mis_pedidos'))
		self.pedido.refresh_from_db()
		self.assertEqual(self.pedido.estado, 'pagado')
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 3)

	def test_cancelar_pedido_devuelve_productos_al_stock(self):
		response = self.client.post(
			reverse('cancelar_pedido', args=[self.pedido.id]),
		)

		self.assertRedirects(response, reverse('mis_pedidos'))
		self.pedido.refresh_from_db()
		self.assertEqual(self.pedido.estado, 'cancelado')
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 5)
		self.assertFalse(Ventas_detalles.objects.filter(pedido=self.pedido).exists())


class CheckoutVentaTests(TestCase):
	def test_checkout_crea_venta_por_producto_del_pedido(self):
		user = User.objects.create_user(username='comprador', password='ClaveSegura123!')
		cliente = Cliente.objects.create(usuario=user)
		producto = Productos.objects.create(
			nombre_producto='Bujía', marca_producto='Auto', precio='12.50', stock=5,
		)
		from .models import Carrito
		Carrito.objects.create(cliente=cliente, producto=producto, cantidad=2)
		self.client.force_login(user)

		response = self.client.post(
			reverse('checkout'), {'metodo_pago': 'tarjeta'}
		)

		self.assertRedirects(response, reverse('mis_pedidos'))
		pedido = Pedido.objects.get(cliente=cliente)
		venta = Ventas_detalles.objects.get(pedido=pedido)
		self.assertEqual(venta.cliente, cliente)
		self.assertEqual(venta.producto, producto)
		self.assertEqual(venta.monto, 25.0)
		self.assertEqual(venta.forma_de_pago, 'tarjeta')
		producto.refresh_from_db()
		self.assertEqual(producto.stock, 3)
