"""
Serializers por el API view de User
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

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

    def update(self, instance, validated_data):
        """Modifica y retorna el usuario"""
        pswd = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if pswd:
            user.set_password(pswd)

        user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer para la autenticación de usuario con token"""
    correo = serializers.EmailField()
    password = serializers.CharField(
        style={'input-type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Valida y autentica el usuario"""
        correo = attrs.get('correo')
        passw = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=correo,
            password=passw,
        )
        if not user:
            msg = _("""No se ha podido autenticar con las
            credenciales provistas""")
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
