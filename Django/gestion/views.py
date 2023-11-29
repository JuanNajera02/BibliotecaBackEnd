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
from .models import TipoUsuario
from .serializers import TipoUsuarioSerializer
from django.db.models import Count, Sum, Case, When, IntegerField
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models import OuterRef, Subquery



class RDUViewSet(viewsets.ModelViewSet):
    queryset = RDU.objects.all()
    serializer_class = RDUSerializer

    ## http://127.0.0.1:8000/gestion/rdus/generarReporteFront?fecha_inicio=2023-01-01&fecha_fin=2023-12-31
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

        result = self.generate_report(stats_am, stats_pm, stats_general)

        return Response(result)

    def get_statistics(self, queryset):
        # Obtener tipos de usuario únicos para cada facultad y carrera
        tipos_usuario_stats = queryset.values(
            'id_carrera__nombre',
            'id_carrera__facultad__nombre',
            'tipoUsuario__nombre'
        ).annotate(
            total=Count('id')
        ).values(
            'id_carrera__nombre',
            'id_carrera__facultad__nombre',
            'tipoUsuario__nombre',
            'total'
        )

        # Estadísticas por facultad y carrera
        stats_facultad_carrera = queryset.values(
            'id_carrera__nombre',
            'id_carrera__facultad__nombre',
        ).annotate(
            total=Count('id'),
            hombres=Coalesce(
                Sum(Case(When(sexo='MASCULINO', then=1), default=0, output_field=IntegerField())),
                0
            ),
            mujeres=Coalesce(
                Sum(Case(When(sexo='FEMENINO', then=1), default=0, output_field=IntegerField())),
                0
            ),
        )

        return {
            'facultad_carrera': [
                {
                    'id_carrera__nombre': entry['id_carrera__nombre'],
                    'id_carrera__facultad__nombre': entry['id_carrera__facultad__nombre'],
                    'total': entry['total'],
                    'hombres': entry['hombres'],
                    'mujeres': entry['mujeres'],
                    'tipos_usuario': [
                        {
                            'nombre': tipo_entry['tipoUsuario__nombre'],
                            'total': tipo_entry['total'],
                        } for tipo_entry in tipos_usuario_stats
                        if tipo_entry['id_carrera__nombre'] == entry['id_carrera__nombre'] and
                        tipo_entry['id_carrera__facultad__nombre'] == entry['id_carrera__facultad__nombre']
                    ],
                } for entry in stats_facultad_carrera
            ],
            'sexo': {
                'hombres': stats_facultad_carrera.aggregate(Sum('hombres'))['hombres__sum'] or 0,
                'mujeres': stats_facultad_carrera.aggregate(Sum('mujeres'))['mujeres__sum'] or 0,
            },
        }

    def generate_report(self, stats_am, stats_pm, stats_general):
        # Aquí construyes el informe como desees
        # Puedes usar las variables stats_am, stats_pm y stats_general
        # para obtener la información necesaria y construir el informe

        # Obtener totales de tipos de usuario en la mañana, tarde y en general
        total_tipos_usuario_am = self.get_total_tipos_usuario(stats_am)
        total_tipos_usuario_pm = self.get_total_tipos_usuario(stats_pm)
        total_tipos_usuario_general = self.get_total_tipos_usuario(stats_general)

        report = {
            'mañana': {
                'stats': stats_am,
                'total_tipos_usuario': total_tipos_usuario_am,
            },
            'tarde': {
                'stats': stats_pm,
                'total_tipos_usuario': total_tipos_usuario_pm,
            },
            'general': {
                'stats': stats_general,
                'total_tipos_usuario': total_tipos_usuario_general,
            }
        }

        return report

    def get_total_tipos_usuario(self, stats):
        # Obtener totales de tipos de usuario en la mañana, tarde y en general
        total_tipos_usuario = stats['facultad_carrera'][0]['tipos_usuario']
        for entry in stats['facultad_carrera'][1:]:
            for tipo_usuario in entry['tipos_usuario']:
                tipo_usuario_entry = next(
                    (t for t in total_tipos_usuario if t['nombre'] == tipo_usuario['nombre']),
                    None
                )
                if tipo_usuario_entry:
                    tipo_usuario_entry['total'] += tipo_usuario['total']
                else:
                    total_tipos_usuario.append({
                        'nombre': tipo_usuario['nombre'],
                        'total': tipo_usuario['total'],
                    })

        return total_tipos_usuario
    
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
            return Response({'nombre': usuario_obj.nombre, 'mensaje': 'Exito'})
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado o contraseña incorrecta'}, status=404)
    
class TipoUsuarioViewSet(viewsets.ModelViewSet):
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer