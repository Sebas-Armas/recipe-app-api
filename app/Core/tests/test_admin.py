"""
Test para modificaciones de admin Django
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Pruebas para admin Django"""

    def setUp(self):
        """Crear usuario y cliente"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            correo='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            correo='user1@example.com',
            password='testpass123',
            nombre='Usuario Prueba'
        )

    def test_usuario_lista(self):
        """Prueba que los usuarios están listados en la página"""
        url = reverse('admin:Core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.nombre)
        self.assertContains(res, self.user.correo)

    def test_pagina_editar_usuario(self):
        """Prueba si funciona la página de editar usuario"""
        url = reverse('admin:Core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_pagina_agregar_usuario(self):
        """Prueba si funciona la página de crear usuario"""
        url = reverse('admin:Core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
