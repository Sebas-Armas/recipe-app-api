"""
Pruebas para el API de Ingredientes
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from Core.models import Ingrediente

from receta.serializers import (
    IngredienteSerializer,
)

INGREDIENTE_URL = reverse('receta:ingrediente-list')


def detail_url(ingrediente_id):
    """Crea y retorna una url del detalle de ingredientes"""
    return reverse('receta:ingrediente-detail', args=[ingrediente_id])


def crear_usuario(correo='user@example.com', password='testpass123'):
    """Crea y retoirna un nuevo usuario"""
    return get_user_model().objects.create_user(correo, password)


class PublicIngredienteAPITests(TestCase):
    """Pruebas para peticiones API sin autenticar"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requerida(self):
        """Prueba que la autenticación sea requerida para llamar al API"""
        res = self.client.get(INGREDIENTE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredienteAPITests(TestCase):
    """Pruebas para peticiones API con autenticación"""

    def setUp(self):
        self.user = crear_usuario()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_recuperar_ingredientes(self):
        """Prueba de recuperación de una lista de ingredientes"""
        Ingrediente.objects.create(user=self.user, nombre="Sal")
        Ingrediente.objects.create(user=self.user, nombre="Pimienta")

        res = self.client.get(INGREDIENTE_URL)

        ingredientes = Ingrediente.objects.all().order_by("-nombre")
        serializer = IngredienteSerializer(ingredientes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredientes_limitados_por_usuario(self):
        """Prueba la recuperación de una lista de ingredientes
            Limitada por el usuario autenticado
        """
        otro_user = crear_usuario(
            correo='otro@example.com',
        )
        Ingrediente.objects.create(user=otro_user, nombre='Sal')
        ingrediente = Ingrediente.objects.create(
            user=self.user,
            nombre='Tomate'
        )

        res = self.client.get(INGREDIENTE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['nombre'], ingrediente.nombre)
        self.assertEqual(res.data[0]['id'], ingrediente.id)

    def test_modificar_ingrediente(self):
        """Prueba de modificación del ingrediente"""
        ingrediente = Ingrediente.objects.create(
            user=self.user,
            nombre='Cilantro'
        )

        payload = {'nombre': 'Perejil'}
        url = detail_url(ingrediente.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingrediente.refresh_from_db()
        self.assertEqual(ingrediente.nombre, payload['nombre'])

    def test_eliminar_ingrediente(self):
        """Prueba la eleminacón de un ingrediente"""
        ingrediente = Ingrediente.objects.create(
            user=self.user,
            nombre='Lechuga'
        )

        url = detail_url(ingrediente.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Ingrediente.objects.filter(nombre=ingrediente.nombre).exists()
        )
