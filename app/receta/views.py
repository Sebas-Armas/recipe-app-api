"""
Views para el API de Receta
"""

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from Core.models import Receta, Tag, Ingrediente
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
        elif self.action == 'upload_image':
            return serializers.RecetaImagenSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Crea una nueva receta"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Carga una imagen a la receta"""
        receta = self.get_object()
        serializer = self.get_serializer(receta, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecetaAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Clase Base para TagViewSet y IngredienteViewSet"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Recupera los tags del usuario autenticado"""
        return self.queryset.filter(user=self.request.user).order_by('-nombre')


class TagViewSet(BaseRecetaAttrViewSet):
    """Vista para gestionar APIs Tags"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredienteViewSet(BaseRecetaAttrViewSet):
    """Vista para gestionar APIs Ingredientes"""
    serializer_class = serializers.IngredienteSerializer
    queryset = Ingrediente.objects.all()
