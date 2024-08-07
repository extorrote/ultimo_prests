# Generated by Django 5.0.7 on 2024-08-01 17:07

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgregarBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_base', models.CharField(max_length=200)),
                ('monto_base', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AgregarGasto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_gasto', models.CharField(max_length=200)),
                ('monto_gasto', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('monto', models.IntegerField()),
                ('monto_mas_interes', models.DecimalField(decimal_places=2, max_digits=10)),
                ('couta_diaria', models.DecimalField(decimal_places=2, max_digits=10)),
                ('saldo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('direccion', models.CharField(max_length=100)),
                ('descripcion_casa', models.TextField(default='null', verbose_name='Descripción de la Casa')),
                ('foto_casa', models.ImageField(default='null', upload_to='articulos', verbose_name='Foto de la Casa')),
                ('fecha_de_creacion', models.DateTimeField(auto_now_add=True)),
                ('ultima_fecha_de_edicion', models.DateTimeField(auto_now=True)),
                ('order', models.SmallIntegerField(default=0, verbose_name='Orden')),
            ],
            options={
                'verbose_name': 'Tu cliente',
                'verbose_name_plural': 'Tus Clientes',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paquete2.cliente')),
            ],
        ),
    ]