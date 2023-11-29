from django.db import models

class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

class Carrera(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE)


class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    usuario = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)

class RDU(models.Model):
    SEXO_CHOICES = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    tipoUsuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)
    fechayhora = models.DateTimeField()  # Cambio de TimeField a DateTimeField
    id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)