# Generated by Django 4.1.7 on 2023-05-08 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_alter_product_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description_product',
            field=models.CharField(default=None, max_length=1000),
        ),
    ]
