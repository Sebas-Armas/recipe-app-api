"""
Serializers para las APIs recetas
"""

from rest_framework import serializers

from Core.models import Receta, Tag, Ingrediente


class IngredienteSerializer(serializers.ModelSerializer):
    """Serializer para Ingredientes"""

    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer para Tags"""

    class Meta:
        model = Tag
        fields = ['id', 'nombre']
        read_only_fields = ['id']


class RecetaSerializer(serializers.ModelSerializer):
    """Serializer para Recetas"""
    tags = TagSerializer(many=True, required=False)
    ingredientes = IngredienteSerializer(many=True, required=False)

    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'tiempo_minutos', 'precio', 'link', 'tags',
            'ingredientes'
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, receta):
        """Maneja obtención o creación de tags como sea necesario"""
        auth_user = self.context['request'].user
        for t in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **t,
            )
            receta.tags.add(tag_obj)

    def _get_or_create_ingredientes(self, ingredientes, receta):
        """Maneja obtención o creación de ingredientes como sea necesario"""
        auth_user = self.context['request'].user
        for i in ingredientes:
            ing_obj, created = Ingrediente.objects.get_or_create(
                user=auth_user,
                **i,
            )
            receta.ingredientes.add(ing_obj)

    def create(self, validated_data):
        """Crea una Receta"""
        tags = validated_data.pop('tags', [])
        ingredientes = validated_data.pop('ingredientes', [])
        receta = Receta.objects.create(**validated_data)
        self._get_or_create_tags(tags, receta)
        self._get_or_create_ingredientes(ingredientes, receta)

        return receta

    def update(self, instance, validated_data):
        """Modifica una receta"""
        tags = validated_data.pop('tags', None)
        ingredientes = validated_data.pop('ingredientes', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredientes is not None:
            instance.ingredientes.clear()
            self._get_or_create_ingredientes(ingredientes, instance)

        for attr, vlaue in validated_data.items():
            setattr(instance, attr, vlaue)

        instance.save()
        return instance


class RecetaDetailSerializer(RecetaSerializer):
    """Serializer para la vista de detalle"""

    class Meta(RecetaSerializer.Meta):
        fields = RecetaSerializer.Meta.fields + ['desc']
