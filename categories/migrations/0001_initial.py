# Generated by Django 3.2.5 on 2021-07-28 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('category_of', models.CharField(choices=[('POS', 'Posts'), ('PRO', 'Products')], max_length=3)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='categories.category')),
            ],
            options={
                'db_table': 'Categories',
            },
        ),
    ]