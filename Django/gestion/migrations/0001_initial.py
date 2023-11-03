# Generated by Django 4.2.7 on 2023-11-01 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Carrera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Facultad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RDU',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('sexo', models.CharField(choices=[('MASCULINO', 'Masculino'), ('FEMENINO', 'Femenino')], max_length=10)),
                ('tipoUsuario', models.CharField(choices=[('INTERNO', 'Interno'), ('EXTERNO', 'Externo')], max_length=10)),
                ('fechayhora', models.TimeField()),
                ('id_carrera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.carrera')),
                ('id_facultad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.facultad')),
            ],
        ),
    ]