# Generated by Django 4.2.7 on 2023-11-29 03:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0004_tipousuario_remove_usuario_nombrecompleto_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rdu',
            name='apellidos',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]