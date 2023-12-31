# Generated by Django 4.2.7 on 2023-11-30 23:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0012_remove_rdu_id_facultad'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Usuario',
            new_name='Administradores',
        ),
        migrations.RemoveField(
            model_name='rdu',
            name='fechayhora',
        ),
        migrations.AddField(
            model_name='rdu',
            name='matricula',
            field=models.CharField(default=12345678, max_length=8, unique=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Visitias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechayhora', models.DateTimeField()),
                ('idRDU', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.rdu')),
            ],
        ),
    ]
