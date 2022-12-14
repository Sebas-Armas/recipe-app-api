"""
Pruebas para el API de Tags
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from Core.models import Tag, Receta

from receta.serializers import (
    TagSerializer,
)

TAGS_URL = reverse('receta:tag-list')


def detail_url(tag_id):
    """Crea y retorna una url del detalle de tag"""
    return reverse('receta:tag-detail', args=[tag_id])


def crear_usuario(correo='user@example.com', password='testpass123'):
    """Crea y retoirna un nuevo usuario"""
    return get_user_model().objects.create_user(correo, password)


class PublicTagAPITests(TestCase):
    """Pruebas para peticiones API sin autenticar"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requerida(self):
        """Prueba que la autenticación sea requerida para llamar al API"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Pruebas para peticiones API con autenticación"""

    def setUp(self):
        self.user = crear_usuario()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_recuperar_tags(self):
        """Prueba la recuperación de una lista de tags"""
        Tag.objects.create(user=self.user, nombre='Vegano')
        Tag.objects.create(user=self.user, nombre='Postre')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-nombre')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_lista_tags_limitada_por_usuario(self):
        """Prueba la recuperación de una lista de tags
            Limitada por el usuario autenticado
        """
        otro_user = crear_usuario(
            correo='otro@example.com',
        )
        Tag.objects.create(user=otro_user, nombre='Vegano')
        tag = Tag.objects.create(user=self.user, nombre='Postre')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['nombre'], tag.nombre)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_modificar_tag(self):
        """Prueba de modificación del tag"""
        tag = Tag.objects.create(user=self.user, nombre='Merienda')

        payload = {'nombre': 'Postre'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.nombre, payload['nombre'])

    def test_eliminar_tag(self):
        """Prueba la eleminacón de un tag"""
        tag = Tag.objects.create(user=self.user, nombre='Merienda')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(nombre=tag.nombre).exists())

    def test_filtro_tags_asignados_a_recetas(self):
        """Prueba el listado de igredientes que
        se encuentran asignados a recetas"""
        tag1 = Tag.objects.create(user=self.user, nombre='Desayuno')
        tag2 = Tag.objects.create(user=self.user, nombre='Lunch')
        receta = Receta.objects.create(
            titulo='Waffles',
            tiempo_minutos=15,
            precio=Decimal('6.40'),
            user=self.user
        )
        receta.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'asignado': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtrado_tags_unicos(self):
        """Prueba que los tags filtrados no
        se repitan"""
        tag = Tag.objects.create(user=self.user, nombre='Costa')
        Tag.objects.create(user=self.user, nombre='Sierra')
        receta1 = Receta.objects.create(
            titulo='Ceviche',
            tiempo_minutos=45,
            precio=Decimal('16.78'),
            user=self.user
        )
        receta2 = Receta.objects.create(
            titulo='Encebollado',
            tiempo_minutos=34,
            precio=Decimal('5.50'),
            user=self.user
        )

        receta1.tags.add(tag)
        receta2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'asignado': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
