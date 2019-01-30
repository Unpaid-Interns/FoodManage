# Generated by Django 2.1.5 on 2019-01-30 22:49

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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Ingredient Name')),
                ('number', models.IntegerField(blank=True, unique=True, verbose_name='Ingredient#')),
                ('vendor_info', models.TextField(blank=True, verbose_name='Vendor Information')),
                ('package_size', models.CharField(max_length=256)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('comment', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='IngredientQty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=10, max_digits=20)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sku_manage.Ingredient')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('sku_num', models.IntegerField(blank=True, unique=True, verbose_name='SKU#')),
                ('case_upc', models.DecimalField(decimal_places=0, max_digits=12, unique=True, verbose_name='Case UPC')),
                ('unit_upc', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='Unit UPC')),
                ('unit_size', models.CharField(max_length=256)),
                ('units_per_case', models.IntegerField()),
                ('comment', models.TextField(blank=True)),
                ('product_line', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sku_manage.ProductLine')),
            ],
        ),
        migrations.AddField(
            model_name='ingredientqty',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sku_manage.SKU'),
        ),
    ]
