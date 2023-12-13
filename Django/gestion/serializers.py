from rest_framework import serializers
from .models import RDU
from .models import Facultad
from .models import Carrera
from .models import Administradores
from .models import TipoUsuario
from .models import Visitias


class RDUSerializer(serializers.ModelSerializer):
    nombre_carrera = serializers.SerializerMethodField()
    id_facultad = serializers.SerializerMethodField()

    class Meta:
        model = RDU
        fields = ['id', 'matricula', 'nombre', 'apellidos', 'sexo', 'tipoUsuario', 'id_carrera', 'nombre_carrera', 'id_facultad']

    def get_nombre_carrera(self, obj):
        return obj.id_carrera.nombre if obj.id_carrera else None

    def get_id_facultad(self, obj):
        return obj.id_carrera.facultad.id if obj.id_carrera and obj.id_carrera.facultad else None

class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = '__all__'

class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = '__all__'

class AdministradoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administradores
        fields = '__all__'

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = '__all__'
    
class VisitiasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitias
        fields = '__all__'