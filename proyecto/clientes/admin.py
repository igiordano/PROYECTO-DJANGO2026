from django.contrib import admin
from .models import Cliente, Carrito, Pedido, DetallePedido

admin.site.register(Cliente)
admin.site.register(Carrito)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
