# Generated by Django 4.1.7 on 2023-05-08 12:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0003_alter_block_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='timestamp',
            field=models.TextField(default=datetime.date(2023, 5, 8)),
        ),
    ]
