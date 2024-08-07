# Generated by Django 5.0.7 on 2024-08-04 02:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prestamosapp', '0007_alter_cliente_couta_diaria_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agregarbase',
            options={'ordering': ['created_at'], 'verbose_name': 'Base', 'verbose_name_plural': 'Historial de Bases'},
        ),
        migrations.AlterModelOptions(
            name='agregargasto',
            options={'ordering': ['created_at'], 'verbose_name': 'Gasto', 'verbose_name_plural': 'Gastos'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['payment_date'], 'verbose_name': 'Pago', 'verbose_name_plural': 'Pagos'},
        ),
    ]