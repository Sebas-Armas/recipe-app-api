"""
Views para el API de Receta
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from Core.models import Receta, Tag, Ingrediente
from receta import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Lista de tags IDs separados por coma para filtrar'
            ),
            OpenApiParameter(
                'ingredientes',
                OpenApiTypes.STR,
                description="""Lista de ingredientes IDs separados
                por coma para filtrar"""
            )
        ]
    )
)
class RecetaViewSet(viewsets.ModelViewSet):
    """Vista para gestionar APIs recetas"""
    serializer_class = serializers.RecetaDetailSerializer
    queryset = Receta.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convierte una lista de strings a enteros"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Recupera las recetas del usuario autenticado"""
        tags = self.request.query_params.get('tags')
        ingredientes = self.request.query_params.get('ingredientes')
        queryset = self.queryset
        if tags:
            tags_id = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_id)
        if ingredientes:
            ing_id = self._params_to_ints(ingredientes)
            queryset = queryset.filter(ingredientes__id__in=ing_id)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'asignado',
                OpenApiTypes.INT,
                enum=[0, 1],
                description='Filtra por items asigandos a la receta'
            ),
        ]
    )
)
class BaseRecetaAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Clase Base para TagViewSet y IngredienteViewSet"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Recupera los tags del usuario autenticado"""
        asignado = bool(
            int(self.request.query_params.get('asignado', 0))
        )
        queryset = self.queryset
        if asignado:
            queryset = queryset.filter(receta__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-nombre').distinct()


class TagViewSet(BaseRecetaAttrViewSet):
    """Vista para gestionar APIs Tags"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredienteViewSet(BaseRecetaAttrViewSet):
    """Vista para gestionar APIs Ingredientes"""
    serializer_class = serializers.IngredienteSerializer
    queryset = Ingrediente.objects.all()
