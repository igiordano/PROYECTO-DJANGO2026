from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Autopartes', '0002_productos_precio_productos_stock'),
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ventas_detalles',
            name='usuario',
        ),
        migrations.AddField(
            model_name='ventas_detalles',
            name='cliente',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='clientes.cliente',
            ),
        ),
    ]