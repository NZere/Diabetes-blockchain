# Generated by Django 4.1.7 on 2023-04-29 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='all_work_times',
            name='date',
            field=models.DateField(),
        ),
    ]
