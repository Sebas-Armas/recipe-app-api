"""
Sample test
"""

from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """Test del módulo calc."""

    def test_suma_numeros(self):
        """Prueba de sumna de números"""
        res = calc.suma(5,6)

        self.assertEqual(res, 11)

    def test_resta_numeros(self):
        """Prueba de sumna de números"""
        res = calc.resta(10,5)

        self.assertEqual(res, 5)
