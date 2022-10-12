"""
Views para el API de Receta
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from Core.models import Receta
from receta import serializers


class RecetaViewSet(viewsets.ModelViewSet):
    """Vista para gestionar APIs recetas"""
    serializer_class = serializers.RecetaDetailSerializer
    queryset = Receta.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Recupera las recetas del usuario autenticado"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Recupera la clase serializer para la petición"""
        if self.action == 'list':
            return serializers.RecetaSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Crea una nueva receta"""
        serializer.save(user=self.request.user)
