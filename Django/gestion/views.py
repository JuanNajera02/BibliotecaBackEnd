from rest_framework import viewsets
from django.db.models import Count
from django.db.models.functions import TruncHour
from django.utils import timezone
from rest_framework.decorators import action
from .models import RDU
from rest_framework.response import Response
from .serializers import RDUSerializer
from .models import Facultad
from .serializers import FacultadSerializer
from .models import Carrera
from .serializers import CarreraSerializer
from .models import Usuario
from .serializers import UsuarioSerializer

class RDUViewSet(viewsets.ModelViewSet):
    queryset = RDU.objects.all()
    serializer_class = RDUSerializer


    @action(detail=False, methods=['GET'])
    def generarReporteFront(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        fecha_inicio = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d').date() if fecha_inicio else None
        fecha_fin = timezone.datetime.strptime(fecha_fin, '%Y-%m-%d').date() if fecha_fin else None

        if fecha_inicio and fecha_fin:
            rdu_records = RDU.objects.filter(fechayhora__date__range=[fecha_inicio, fecha_fin])
        else:
            rdu_records = RDU.objects.all()

        rdu_am = rdu_records.filter(fechayhora__hour__lt=12)
        rdu_pm = rdu_records.filter(fechayhora__hour__gte=12)

        stats_am = self.get_statistics(rdu_am)
        stats_pm = self.get_statistics(rdu_pm)
        stats_general = self.get_statistics(rdu_records)

        result = {
            'mañana': stats_am,
            'tarde': stats_pm,
            'general': stats_general
        }

        return Response(result)

    def get_statistics(self, queryset):
        stats_facultad_carrera = queryset.values('id_carrera__nombre').annotate(
            total=Count('id')
        )

        stats_sexo = queryset.values('sexo').annotate(
            total=Count('id')
        )

        return {
            'facultad_carrera': stats_facultad_carrera,
            'sexo': stats_sexo
        }
    
    @action(detail=True, methods=['PUT'])
    def update_record(self, request, pk=None):
        rdu_instance = self.get_object()
        serializer = RDUSerializer(rdu_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    
class FacultadViewSet(viewsets.ModelViewSet):
    queryset = Facultad.objects.all()
    serializer_class = FacultadSerializer

class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=['POST'])
    def validar_usuario(self, request):
        usuario = request.data.get('usuario', None)
        password = request.data.get('password', None)

        if usuario is None or password is None:
            return Response({'error': 'Debes proporcionar usuario y contraseña'}, status=400)

        try:
            usuario_obj = Usuario.objects.get(usuario=usuario, password=password)
            return Response({'nombreCompleto': usuario_obj.nombreCompleto, 'mensaje': 'Éxito'})
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado o contraseña incorrecta'}, status=404)