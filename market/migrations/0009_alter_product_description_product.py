# Generated by Django 4.1.7 on 2023-05-08 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0008_alter_product_description_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description_product',
            field=models.CharField(default=None, max_length=1000, null=True),
        ),
    ]
