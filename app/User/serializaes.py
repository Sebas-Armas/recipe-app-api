"""
Serializers por el API view de User
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el objeto usuario"""

    class Meta:
        model = get_user_model()
        fields = ['correo', 'password', 'nombre']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        """Crea y regresa un usuario con contraseña encriptada"""
        return get_user_model().objects.create_user(**validated_data)
