"""
Pruebas para el API de Recetas
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from Core.models import Receta, Tag, Ingrediente

from receta.serializers import (
    RecetaSerializer,
    RecetaDetailSerializer,
)

RECETAS_URL = reverse('receta:receta-list')


def detail_url(receta_id):
    """Crea y retorna una URL para dl detalle de receta"""
    return reverse('receta:receta-detail', args=[receta_id])


def crear_receta(user, **params):
    """Crea y regresa una receta de muestra"""
    defaults = {
        'titulo': 'Titulo Receta de Muestra',
        'tiempo_minutos': 22,
        'precio': Decimal('5.25'),
        'desc': 'Descripción de ejemplo',
        'link': 'http://example.com/receta.pdf'
    }
    defaults.update(params)

    receta = Receta.objects.create(user=user, **defaults)
    return receta


def crear_usuario(**params):
    """Crea y retoirna un nuevo usuario"""
    return get_user_model().objects.create_user(**params)


class PublicRecetaAPITests(TestCase):
    """Pruebas para peticiones API sin autenticar"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requerida(self):
        """Prueba que la autenticación sea requerida para llamar al API"""
        res = self.client.get(RECETAS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecetaAPITests(TestCase):
    """Pruebas para peticiones API con autenticación"""

    def setUp(self):
        self.user = crear_usuario(
            correo='test@example.com',
            password='testpass123',
            nombre='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_recuperar_recetas(self):
        """Prueba la recuperación de una lista de recetas"""
        crear_receta(user=self.user)
        crear_receta(user=self.user)

        res = self.client.get(RECETAS_URL)

        recetas = Receta.objects.all().order_by('-id')
        serializer = RecetaSerializer(recetas, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_lista_recetas_limitada_por_usuario(self):
        """Prueba la recuperación de una lista de recetas
            Limitada por el usuario autenticado
        """
        otro_user = crear_usuario(
            correo='otro@example.com',
            password='testpass123',
            nombre='Test Otro'
        )
        crear_receta(user=otro_user)
        receta = crear_receta(user=self.user, titulo='receta de usuario único')

        res = self.client.get(RECETAS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['titulo'], receta.titulo)
        self.assertEqual(res.data[0]['id'], receta.id)

    def test_get_receta_detalle(self):
        """Prueba de obtención del detalle de la receta"""
        receta = crear_receta(user=self.user)

        url = detail_url(receta.id)
        res = self.client.get(url)

        serializer = RecetaDetailSerializer(receta)
        self.assertEqual(res.data, serializer.data)

    def test_crear_receta(self):
        """Prueba la creación de una receta"""
        payload = {
            'titulo': 'Titulo Receta de Muestra',
            'tiempo_minutos': 30,
            'precio': Decimal('5.99'),
        }
        res = self.client.post(RECETAS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        receta = Receta.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(receta, k), v)
        self.assertEqual(receta.user, self.user)

    def test_modificacion_parcial(self):
        """Prueba la modificación parcial de una receta"""
        original_link = 'http://example.com/receta.pdf'
        receta = crear_receta(
            user=self.user,
            titulo='Titulo Original',
            link=original_link
        )

        payload = {'titulo': 'Nuevo Titulo'}
        url = detail_url(receta.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        receta.refresh_from_db()
        self.assertEqual(receta.titulo, payload['titulo'])
        self.assertEqual(receta.link, original_link)
        self.assertEqual(receta.user, self.user)

    def test_modificacion_total(self):
        """Prueba la modificación total de una receta"""
        receta = crear_receta(
            user=self.user,
            titulo='Titulo Original',
            link='http://example.com/receta.pdf',
            desc='Descripción original',
        )

        payload = {
            'titulo': 'Nuevo Titulo',
            'link': 'http://example.com/nueva-receta.pdf',
            'desc': 'Nueva Descripción',
            'tiempo_minutos': 10,
            'precio': Decimal('2.50')
        }
        url = detail_url(receta.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        receta.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(receta, k), v)
        self.assertEqual(receta.user, self.user)

    def test_modificar_usuario_error(self):
        """Prueba cambiar el usuario resulta en error"""
        new_user = crear_usuario(
            correo='user2@example.com',
            password='test123'
        )
        receta = crear_receta(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(receta.id)
        self.client.patch(url, payload)

        receta.refresh_from_db()
        self.assertEqual(receta.user, self.user)

    def test_borrar_receta(self):
        receta = crear_receta(user=self.user)

        url = detail_url(receta.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Receta.objects.filter(id=receta.id).exists())

    def test_borrar_receta_otros_usuarios_error(self):
        """Prueba al intentar borrar recetas de otros usuarios da error"""
        new_user = crear_usuario(
            correo='user2@example.com',
            password='test123'
        )
        receta = crear_receta(user=new_user)

        url = detail_url(receta.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Receta.objects.filter(id=receta.id).exists())

    def crear_receta_con_nuevos_tags(self):
        """Prueba la creación de una receta con nuevos tags"""
        payload = {
            'titulo': 'Nuevo Titulo',
            'link': 'http://example.com/nueva-receta.pdf',
            'desc': 'Nueva Descripción',
            'tiempo_minutos': 10,
            'precio': Decimal('2.50'),
            'tags': [{'nombre': 'China'}, {'nombre': 'Cena'}],
        }
        res = self.client.post(RECETAS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recetas = Receta.objects.filter(user=self.user)
        self.assertEqual(recetas.count(), 1)
        receta = recetas[0]
        self.assertEqual(receta.tags.count(), 2)
        for tag in payload['tags']:
            exists = receta.tags.filter(
                nombre=tag['nombre'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_crear_receta_con_tags_existentes(self):
        """Prueba crear una receta con tags existentes"""
        tag_indian = Tag.objects.create(user=self.user, nombre='Indian')
        payload = {
            'titulo': 'Nuevo Titulo',
            'tiempo_minutos': 10,
            'precio': Decimal('2.50'),
            'tags': [{'nombre': 'Indian'}, {'nombre': 'Cena'}],
        }
        res = self.client.post(RECETAS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recetas = Receta.objects.filter(user=self.user)
        self.assertEqual(recetas.count(), 1)
        receta = recetas[0]
        self.assertEqual(receta.tags.count(), 2)
        self.assertIn(tag_indian, receta.tags.all())
        for tag in payload['tags']:
            exists = receta.tags.filter(
                nombre=tag['nombre'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_crear_tag_al_modificar_receta(self):
        """Prueba de crear un Tag al actualizar una receta"""
        receta = crear_receta(user=self.user)

        payload = {
            'tags': [{'nombre': 'Lunch'}],
        }
        url = detail_url(receta.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, nombre='Lunch')
        self.assertIn(new_tag, receta.tags.all())

    def test_modificar_receta_asignar_tag(self):
        """Prueba asignar un tag existente cuando se modifica una receta"""
        tag_indian = Tag.objects.create(user=self.user, nombre='Indian')
        receta = crear_receta(user=self.user)
        receta.tags.add(tag_indian)

        tag_lunch = Tag.objects.create(user=self.user, nombre='Lunch')
        payload = {
            'tags': [{'nombre': 'Lunch'}],
        }
        url = detail_url(receta.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, receta.tags.all())
        self.assertNotIn(tag_indian, receta.tags.all())

    def test_limpiar_tags_de_receta(self):
        """Prueba vaciar el campo de Tags en recetas"""
        tag_indian = Tag.objects.create(user=self.user, nombre='Indian')
        receta = crear_receta(user=self.user)
        receta.tags.add(tag_indian)

        payload = {
            'tags': [],
        }
        url = detail_url(receta.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(receta.tags.count(), 0)

    def crear_receta_con_nuevos_ingredientes(self):
        """Prueba la creación de una receta con nuevos ingredientes"""
        payload = {
            'titulo': 'Alitas BBQ',
            'link': 'http://example.com/nueva-receta.pdf',
            'desc': 'Nueva Descripción',
            'tiempo_minutos': 10,
            'precio': Decimal('12.50'),
            'ingredientes': [{'nombre': 'Alitas'}, {'nombre': 'Salsa BBQ'}],
        }
        res = self.client.post(RECETAS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recetas = Receta.objects.filter(user=self.user)
        self.assertEqual(recetas.count(), 1)
        receta = recetas[0]
        self.assertEqual(receta.ingredientes.count(), 2)
        for ing in payload['ingredientes']:
            exists = receta.ingredientes.filter(
                nombre=ing['nombre'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_crear_receta_con_ingredientes_existentes(self):
        """Prueba crear una receta con ingredientes existentes"""
        ingrediente = Ingrediente.objects.create(
            user=self.user,
            nombre='Limón'
        )
        payload = {
            'titulo': 'Ensalada Tomate y Cebolla',
            'tiempo_minutos': 10,
            'precio': '5.78',
            'ingredientes': [{'nombre': 'Lechuga'}, {'nombre': 'Limón'}],
        }
        res = self.client.post(RECETAS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recetas = Receta.objects.filter(user=self.user)
        self.assertEqual(recetas.count(), 1)
        receta = recetas[0]
        self.assertEqual(receta.ingredientes.count(), 2)
        self.assertIn(ingrediente, receta.ingredientes.all())
        for ing in payload['ingredientes']:
            exists = receta.ingredientes.filter(
                nombre=ing['nombre'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_crear_ingrediente_al_modificar_receta(self):
        """Prueba de crear un Ingrediente al actualizar una receta"""
        receta = crear_receta(user=self.user)

        payload = {
            'ingredientes': [{'nombre': 'Lima'}],
        }
        url = detail_url(receta.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ing = Ingrediente.objects.get(user=self.user, nombre='Lima')
        self.assertIn(new_ing, receta.ingredientes.all())

    def test_modificar_receta_asignar_ingrediente(self):
        """Prueba asignar un ingrediente existente
            cuando se modifica una receta"""
        ing_tomate = Ingrediente.objects.create(
            user=self.user,
            nombre='Tomate'
        )
        receta = crear_receta(user=self.user)
        receta.ingredientes.add(ing_tomate)

        ing_cebolla = Ingrediente.objects.create(
            user=self.user,
            nombre='Cebolla'
        )
        payload = {
            'ingredientes': [{'nombre': 'Cebolla'}],
        }
        url = detail_url(receta.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ing_cebolla, receta.ingredientes.all())
        self.assertNotIn(ing_tomate, receta.ingredientes.all())

    def test_limpiar_ingredientes_de_receta(self):
        """Prueba vaciar el campo de Ingredientes en recetas"""
        ing_tomate = Ingrediente.objects.create(
            user=self.user,
            nombre='Tomate'
        )
        receta = crear_receta(user=self.user)
        receta.ingredientes.add(ing_tomate)

        payload = {
            'ingredientes': [],
        }
        url = detail_url(receta.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(receta.ingredientes.count(), 0)
