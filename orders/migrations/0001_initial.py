# Generated by Django 3.2.6 on 2021-08-06 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_of_products', models.PositiveIntegerField()),
                ('shipping_fee', models.PositiveIntegerField()),
                ('total_price', models.PositiveBigIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_method', models.CharField(choices=[('COD', 'Cash On Delivery'), ('VNP', 'VNPay'), ('MOM', 'Momo')], max_length=3)),
                ('is_paid', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='ProductInOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.PositiveIntegerField()),
                ('image', models.URLField()),
                ('number', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Products_in_orders',
            },
        ),
    ]
