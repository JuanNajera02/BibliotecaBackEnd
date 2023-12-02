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
from .models import Administradores
from .serializers import AdministradoresSerializer
from .models import TipoUsuario
from .serializers import TipoUsuarioSerializer
from .models import Visitias
from .serializers import VisitiasSerializer
from django.db.models import Count, Sum, Case, When, IntegerField
import string
import random
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models import OuterRef, Subquery




class RDUViewSet(viewsets.ModelViewSet):
    queryset = RDU.objects.all()
    serializer_class = RDUSerializer

    def create(self, request, *args, **kwargs):
        matricula = request.data.get('matricula', None)

        if matricula is None:
            # Si la matrícula está vacía, genera una matrícula única
            matricula = self.generar_matricula_unico()
            request.data['matricula'] = matricula

        return super().create(request, *args, **kwargs)

    def generar_matricula_unico(self):
        longitud_matricula = 8
        matricula = self.generar_matricula_aleatoria(longitud_matricula)

        # Verificar si la matrícula ya existe en la base de datos
        while RDU.objects.filter(matricula=matricula).exists():
            matricula = self.generar_matricula_aleatoria(longitud_matricula)

        return matricula

    def generar_matricula_aleatoria(self, longitud):
        caracteres = string.ascii_uppercase + string.digits
        return ''.join(random.choice(caracteres) for _ in range(longitud))
    
class FacultadViewSet(viewsets.ModelViewSet):
    queryset = Facultad.objects.all()
    serializer_class = FacultadSerializer

class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer

class AdministradoresViewSet(viewsets.ModelViewSet):
    queryset = Administradores.objects.all()
    serializer_class = AdministradoresSerializer

    @action(detail=False, methods=['POST'])
    def validar_usuario(self, request):
        usuario = request.data.get('usuario', None)
        password = request.data.get('password', None)

        if usuario is None or password is None:
            return Response({'error': 'Debes proporcionar usuario y contraseña'}, status=400)

        try:
            usuario_obj = Administradores.objects.get(usuario=usuario, password=password)
            return Response({'nombre': usuario_obj.nombre, 'mensaje': 'Exito'})
        except Administradores.DoesNotExist:
            return Response({'error': 'Usuario no encontrado o contraseña incorrecta'}, status=404)
    
class TipoUsuarioViewSet(viewsets.ModelViewSet):
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer


class VisitiasViewSet(viewsets.ModelViewSet):
    queryset = Visitias.objects.all()
    serializer_class = VisitiasSerializer


    @action(detail=False, methods=['GET'])
    def generarReporteFront(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        fecha_inicio = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d').date() if fecha_inicio else None
        fecha_fin = timezone.datetime.strptime(fecha_fin, '%Y-%m-%d').date() if fecha_fin else None

        if fecha_inicio and fecha_fin:
            visitas_records = Visitias.objects.filter(fechayhora__date__range=[fecha_inicio, fecha_fin])
        else:
            visitas_records = Visitias.objects.all()

        visitas_am = visitas_records.filter(fechayhora__hour__lt=12)
        visitas_pm = visitas_records.filter(fechayhora__hour__gte=12)

        stats_am = self.get_statistics(visitas_am, 'mañana')
        stats_pm = self.get_statistics(visitas_pm, 'tarde')
        stats_general = self.get_statistics(visitas_records, 'general')

        result = self.generate_report(stats_am, stats_pm, stats_general)

        return Response(result)

    def get_statistics(self, queryset, horario):
        tipos_usuario_stats = queryset.values(
            'idRDU__id_carrera__nombre',
            'idRDU__id_carrera__facultad__nombre',
            'idRDU__tipoUsuario__nombre'
        ).annotate(
            total=Count('id')
        ).values(
            'idRDU__id_carrera__nombre',
            'idRDU__id_carrera__facultad__nombre',
            'idRDU__tipoUsuario__nombre',
            'total'
        )

        stats_facultad_carrera = queryset.values(
            'idRDU__id_carrera__nombre',
            'idRDU__id_carrera__facultad__nombre',
        ).annotate(
            total=Count('id'),
            hombres=Coalesce(
                Sum(Case(When(idRDU__sexo='MASCULINO', then=1), default=0, output_field=IntegerField())),
                0
            ),
            mujeres=Coalesce(
                Sum(Case(When(idRDU__sexo='FEMENINO', then=1), default=0, output_field=IntegerField())),
                0
            ),
        )

        return {
            'facultad_carrera': [
                {
                    'id_carrera__nombre': entry['idRDU__id_carrera__nombre'],
                    'id_carrera__facultad__nombre': entry['idRDU__id_carrera__facultad__nombre'],
                    'total': entry['total'],
                    'hombres': entry['hombres'],
                    'mujeres': entry['mujeres'],
                    'tipos_usuario': [
                        {
                            'nombre': tipo_entry['idRDU__tipoUsuario__nombre'],
                            'total': tipo_entry['total'],
                        } for tipo_entry in tipos_usuario_stats
                        if tipo_entry['idRDU__id_carrera__nombre'] == entry['idRDU__id_carrera__nombre'] and
                        tipo_entry['idRDU__id_carrera__facultad__nombre'] == entry['idRDU__id_carrera__facultad__nombre']
                    ],
                } for entry in stats_facultad_carrera
            ],
            'sexo': {
                'hombres': stats_facultad_carrera.aggregate(Sum('hombres'))['hombres__sum'] or 0,
                'mujeres': stats_facultad_carrera.aggregate(Sum('mujeres'))['mujeres__sum'] or 0,
                'total': stats_facultad_carrera.aggregate(Sum('total'))['total__sum'] or 0,
            },
            'horario': horario,
        }

    def generate_report(self, stats_am, stats_pm, stats_general):
        total_tipos_usuario_am = self.get_total_tipos_usuario(stats_am)
        total_tipos_usuario_pm = self.get_total_tipos_usuario(stats_pm)
        total_tipos_usuario_general = self.get_total_tipos_usuario(stats_general)

        # Eliminar la sección "horario" del diccionario
        stats_am.pop('horario', None)
        stats_pm.pop('horario', None)
        stats_general.pop('horario', None)

        # Agregar el total de registros de hombres y mujeres en lugar de "horario"
        total_hombres = (
            stats_am['sexo']['hombres']
            + stats_pm['sexo']['hombres']
            + stats_general['sexo']['hombres']
        )
        total_mujeres = (
            stats_am['sexo']['mujeres']
            + stats_pm['sexo']['mujeres']
            + stats_general['sexo']['mujeres']
        )

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
        total_tipos_usuario = []

        for entry in stats['facultad_carrera']:
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
