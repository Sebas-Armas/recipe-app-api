"""
Modelos de DB
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager para los usuarios"""

    def create_user(self, email, password=None, **extra_fields):
        """Crea, guarda y regresa un nuevo usuario"""
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        user = self.model(correo=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # Los nombres de los campos deben ser iguales a los
    # atributos del modelo al crear superusuario por cli
    def create_superuser(self, correo, password):
        """Crea, guarda y regresa el superusuario"""
        user = self.create_user(email=correo, password=password)
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
