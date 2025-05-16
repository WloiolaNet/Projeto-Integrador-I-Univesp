from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Cria grupos de usuários e atribui permissões"

    def handle(self, *args, **kwargs):
        grupos_permissoes = {
            'Administrador': [
                'can_add_produto', 'can_edit_produto', 'can_delete_produto', 'can_view_produto',
                'can_add_movimentoproduto', 'can_edit_movimentoproduto', 'can_delete_movimentoproduto', 'can_view_movimentoproduto',
                'can_add_usuario', 'can_edit_usuario', 'can_delete_usuario', 'can_view_usuario',
            ],
            'Vendedor': [
                'can_view_produto', 'can_add_movimentoproduto',
            ],
            'Estoquista': [
                'can_view_produto', 'can_edit_movimentoproduto',
            ],
        }

        for nome_grupo, permissoes in grupos_permissoes.items():
            grupo, created = Group.objects.get_or_create(name=nome_grupo)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Grupo '{nome_grupo}' criado!"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Grupo '{nome_grupo}' já existia."))

            for perm in permissoes:
                permissao = Permission.objects.filter(codename=perm).first()
                if permissao:
                    grupo.permissions.add(permissao)
            
            self.stdout.write(self.style.SUCCESS(f"✔️ Permissões adicionadas ao grupo '{nome_grupo}'."))

