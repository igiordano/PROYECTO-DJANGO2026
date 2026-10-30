from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Autopartes', '0003_ventas_detalles_cliente'),
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventas_detalles',
            name='pedido',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='clientes.pedido',
            ),
        ),
    ]