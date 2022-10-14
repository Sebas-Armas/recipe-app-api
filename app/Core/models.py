"""
Modelos de DB
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager para los usuarios"""

    def create_user(self, correo, password=None, **extra_fields):
        """Crea, guarda y regresa un nuevo usuario"""
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico")
        user = self.model(correo=self.normalize_email(correo), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # Los nombres de los campos deben ser iguales a los
    # atributos del modelo al crear superusuario por cli
    def create_superuser(self, correo, password):
        """Crea, guarda y regresa el superusuario"""
        user = self.create_user(correo=correo, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User que utilizará el proyecto"""
    correo = models.EmailField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'correo'


class Receta(models.Model):
    """Objeto Receta"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    titulo = models.CharField(max_length=255)
    tiempo_minutos = models.IntegerField()
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    desc = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.titulo


class Tag(models.Model):
    """Tags para filtrar recetas"""
    nombre = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.nombre
