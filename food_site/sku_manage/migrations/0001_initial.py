# Generated by Django 2.1.5 on 2019-01-20 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('name', models.CharField(max_length=256, unique=True)),
                ('number', models.AutoField(primary_key=True, serialize=False)),
                ('vendor_info', models.TextField()),
                ('package_size', models.CharField(max_length=256)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductLine',
            fields=[
                ('name', models.CharField(max_length=256, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='SKU',
            fields=[
                ('name', models.CharField(max_length=32)),
                ('sku_num', models.AutoField(primary_key=True, serialize=False)),
                ('case_upc', models.DecimalField(decimal_places=0, max_digits=12, unique=True)),
                ('unit_upc', models.DecimalField(decimal_places=0, max_digits=12)),
                ('unit_size', models.CharField(max_length=256)),
                ('units_per_case', models.IntegerField()),
                ('comment', models.TextField()),
                ('ingredients', models.ManyToManyField(to='sku_manage.Ingredient')),
                ('product_line', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sku_manage.ProductLine')),
            ],
        ),
    ]