"""
Prueba para chequear el estado de salud del API
"""

from django.test import TestCase
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTest(TestCase):
    """Prueba el chequeo de salud del API"""

    def test_health_check(self):
        """Prueba chequeo de salid del API"""
        client = APIClient()
        url = reverse('health-check')
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
