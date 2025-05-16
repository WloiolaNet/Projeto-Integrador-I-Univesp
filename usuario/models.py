from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import AbstractUser



class Usuario(AbstractUser):
    cargo = models.CharField(max_length=50, blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name="usuario_groups", blank=True)
    #user_permissions = models.ManyToManyField(Permission, related_name="usuario_permissions", blank=True)
    #grupo_personalizado = models.ForeignKey(GrupoPersonalizado, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username

class Meta:
        permissions = [
            ("add_usuario", "Can add Usuario"),
            ("change_usuario", "Can change Usuario"),
            ("delete_usuario", "Can delete Usuario"),
            ("view_usuario", "Can view Usuario"),
        ]