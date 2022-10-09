"""
Pruebas para el API de User
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def crear_usuario(**params):
    """Crea y regresa un nuevo usuario"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Prueba las características publicas del API User"""

    def setUp(self):
        self.client = APIClient()

    def test_crear_usuario_exitoso(self):
        """Prueba la creación exitosa de un usuario"""
        payload = {
            'correo': 'test@example.com',
            'password': 'testpass123',
            'nombre': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(correo=payload['correo'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_crear_usuario_con_correo_existente(self):
        """Prueba la creación fallida de un usuario con
            un correo que ya se encuentra en la BD"""
        payload = {
            'correo': 'test@example.com',
            'password': 'testpass123',
            'nombre': 'Test Name',
        }
        crear_usuario(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_usuario_password_corta(self):
        """Prueba la creación de un usuario con
            contraseña menor de 5 caracteres"""
        payload = {
            'correo': 'test@example.com',
            'password': 'pw',
            'nombre': 'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            correo=payload['correo']
        ).exists()
        self.assertFalse(user_exists)
