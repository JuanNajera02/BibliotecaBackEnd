from rest_framework import viewsets
from .models import RDU
from rest_framework.response import Response
from .serializers import RDUSerializer
from .models import Facultad
from .serializers import FacultadSerializer
from .models import Carrera
from .serializers import CarreraSerializer

class RDUViewSet(viewsets.ModelViewSet):
    queryset = RDU.objects.all()
    serializer_class = RDUSerializer

    def list(self, request):
        # Obtén las fechas de la solicitud GET
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        # Filtra los registros de RDU según las fechas
        if fecha_inicio and fecha_fin:
            rdu_records = RDU.objects.filter(fechayhora__gte=fecha_inicio, fechayhora__lte=fecha_fin)
        else:
            rdu_records = RDU.objects.all()

        # Serializa los registros y envía la respuesta
        serializer = RDUSerializer(rdu_records, many=True)
        return Response(serializer.data)
    
class FacultadViewSet(viewsets.ModelViewSet):
    queryset = Facultad.objects.all()
    serializer_class = FacultadSerializer

class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer

