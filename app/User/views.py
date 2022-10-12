"""
Views para el API de User
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializaes import (
    UserSerializer,
    AuthTokenSerializer
)


class CreateUserView(generics.CreateAPIView):
    """Crea un nuevo usuario en el sistema"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Cre un nuevo token de autenticacion para el usuario"""
    serializer_class = AuthTokenSerializer
    render_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Maneja el usuario autenticado"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Recupera y retorna el usuario autenticado"""
        return self.request.user
