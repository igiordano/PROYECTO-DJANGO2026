from django.contrib.auth.models import User
from django.test import TestCase

from clientes.models import Cliente

from .forms import CrearVentasDetallesForm
from .models import Productos, Ventas_detalles


class CrearVentasDetallesFormTests(TestCase):
	def test_venta_se_asocia_al_cliente_seleccionado(self):
		user = User.objects.create_user(username='cliente_venta', password='ClaveSegura123!')
		cliente = Cliente.objects.create(usuario=user)
		producto = Productos.objects.create(
			nombre_producto='Filtro', marca_producto='Auto', precio='10.00', stock=4,
		)
		form = CrearVentasDetallesForm(data={
			'monto': '20.00',
			'fecha_venta': '2026-09-28',
			'forma_de_pago': 'Efectivo',
			'producto': producto.id,
			'cliente': cliente.id,
		})

		self.assertTrue(form.is_valid(), form.errors)
		venta = form.save()

		self.assertIsInstance(venta, Ventas_detalles)
		self.assertEqual(venta.cliente, cliente)
		self.assertNotIn('usuario', form.fields)
