"""
Pruebas para modelos
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from Core import models


def crear_usuario(email='user@example.com', password='testpass123'):
    """Crea y retoirna un nuevo usuario"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Pruebas de Modelos."""

    def test_crear_usuario_con_correo_exitoso(self):
        """Prueba crear un usuario con un correo de manera exitosa"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            correo=email,
            password=password,
        )

        self.assertEqual(user.correo, email)
        self.assertTrue(user.check_password(password))

    def test_nuevo_usuario_correo_normalizado(self):
        """Prueba que los correos sean normalizados en nuevos usuarios."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, esperado in sample_emails:
            user = get_user_model().objects.create_user(
                correo=email,
                password="password",
            )
            self.assertEqual(user.correo, esperado)

    def test_nuevo_usuario_sin_correo_salta_error(self):
        """Prueba que crear un usuario sin un correo salta un ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_crear_superuser(self):
        """Prueba de creación de un superusuario"""
        user = get_user_model().objects.create_superuser(
            correo='test@example.com',
            password="password",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_crear_receta(self):
        """Prueba de creación de una receta"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        receta = models.Receta.objects.create(
            user=user,
            titulo='Nombre receta de Prueba',
            tiempo_minutos=5,
            precio=Decimal('5.50'),
            desc='Descripción de la receta de prueba.'
        )

        self.assertEqual(str(receta), receta.titulo)

    def test_crear_tag(self):
        """Prueba para crear un Tag"""
        user = crear_usuario()
        tag = models.Tag.objects.create(user=user, nombre='Tag1')

        self.assertEqual(str(tag), tag.nombre)

    def test_crear_ingrediente(self):
        """Prueba para crear un Ingrediente"""
        user = crear_usuario()
        ingrediente = models.Ingrediente.objects.create(
            user=user,
            nombre='Ingrediente 1'
        )

        self.assertEqual(str(ingrediente), ingrediente.nombre)

    @patch('Core.models.uuid.uuid4')
    def test_receta_nombre_archivo_uuid(self, mock_uuid):
        """Prueba la generación de la ruta de la imagen"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.receta_imagen_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/receta/{uuid}.jpg')
