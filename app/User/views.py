"""
Views para el API de User
"""

from rest_framework import generics

from .serializaes import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Crea un nuevo usuario en el sistema"""
    serializer_class = UserSerializer
