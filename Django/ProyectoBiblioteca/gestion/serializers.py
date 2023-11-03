from rest_framework import serializers
from .models import RDU
from .models import Facultad
from .models import Carrera


class RDUSerializer(serializers.ModelSerializer):
    class Meta:
        model = RDU
        fields = '__all__'

class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = '__all__'

class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = '__all__'