"""
Serializers para las APIs recetas
"""

from rest_framework import serializers

from Core.models import Receta


class RecetaSerializer(serializers.ModelSerializer):
    """Serializer para Recetas"""

    class Meta:
        model = Receta
        fields = ['id', 'titulo', 'tiempo_minutos', 'precio', 'link']
        read_only_fields = ['id']


class RecetaDetailSerializer(RecetaSerializer):
    """Serializer para la vista de detalle"""

    class Meta(RecetaSerializer.Meta):
        fields = RecetaSerializer.Meta.fields + ['desc']
