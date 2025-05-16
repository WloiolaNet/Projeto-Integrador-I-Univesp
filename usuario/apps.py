from django.apps import AppConfig
from django.core.management import call_command


class UsuarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuario'

def ready(self):
        from .utils import criar_permissoes_padrao
        criar_permissoes_padrao()
