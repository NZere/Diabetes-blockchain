# Generated by Django 4.1.7 on 2023-04-29 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointment', '0002_alter_all_work_times_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='patient',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
