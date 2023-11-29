from django.urls import path, include
from rest_framework import routers
from gestion import views


router = routers.DefaultRouter()
router.register(r'rdus', views.RDUViewSet)
router.register(r'facultades', views.FacultadViewSet)
router.register(r'carreras', views.CarreraViewSet)
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'tiposusuarios', views.TipoUsuarioViewSet)

urlpatterns = [
    # Otras rutas URL
    path('', include(router.urls)),
]


