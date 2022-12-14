"""
Pruebas para el API de User
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_crear_token_para_usuario(self):
        """Prueba que genere un token para credenciales válidas"""
        user_details = {
            'correo': 'test@example.com',
            'password': 'testpass123',
            'nombre': 'Test Name',
        }
        crear_usuario(**user_details)

        payload = {
            'correo': user_details['correo'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_no_crear_token_credenciales_incorrectas(self):
        """Prueba que se retonre error si las credenciales no son válidas"""
        user_details = {
            'correo': 'test@example.com',
            'password': 'testpass123',
        }
        crear_usuario(**user_details)

        payload = {
            'correo': user_details['correo'],
            'password': 'malpassw',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_token_pswd_vacia(self):
        """Prueba enviando Contraseña vacía, retorna error"""
        payload = {
            'correo': 'test@example.com',
            'password': '',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recuperar_usuario_no_autorizado(self):
        """Prueba que la autenticación sea requerida para los usuarios"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Prueba las características que requieren autenticación del API User"""

    def setUp(self):
        self.user = crear_usuario(
            correo='test@example.com',
            password='testpass123',
            nombre='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_recuperar_usuario_exitoso(self):
        """Recuperar el perfil del usuario logeado"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'nombre': self.user.nombre,
            'correo': self.user.correo,
        })

    def test_post_me_no_permitido(self):
        """Prueba POST no es permitido por el endpoint me"""
        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_modificar_perfil_usuario(self):
        """Prueba de modificación del usuario autenticado"""
        payload = {'nombre': 'Updated name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.nombre, payload['nombre'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
