from django.db import models

class Facultad(models.Model):
    nombre = models.CharField(max_length=100)

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)

class Usuario(models.Model):
    nombreCompleto = models.CharField(max_length=255)
    usuario = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)

class RDU(models.Model):
    SEXO_CHOICES = [
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]

    TIPO_USUARIO_CHOICES = [
        ('INTERNO', 'Interno'),
        ('EXTERNO', 'Externo'),
    ]

    nombre = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    tipoUsuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    fechayhora = models.DateTimeField()  # Cambio de TimeField a DateTimeField
    id_facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE)
    id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)