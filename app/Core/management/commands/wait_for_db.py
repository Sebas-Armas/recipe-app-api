"""
Comando Django para esperar a que la base de datos este disponible
"""
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Comando para esperar por la BBDD"""

    def handle(self, *args, **options):
        """Comienzpo del comando"""
        self.stdout.write('Esperando por nuestra BD.....')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('BD no disponible, esperando 1 segundo....')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Base de Datos Disponible!!'))
