from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def criar_permissoes_padrao():
    """
    Cria permissões personalizadas para os modelos desejados
    """
    modelos = ['produto', 'movimentoproduto', 'usuario']
    
    for modelo in modelos:
        modelo_classe = apps.get_model('app_' + modelo, modelo.capitalize())

        if not modelo_classe:
            print(f"❌ Modelo {modelo} não encontrado.")
            continue
        
        content_type = ContentType.objects.get_for_model(modelo_classe)

        permissoes = [
            ('can_add_' + modelo, 'Pode adicionar ' + modelo),
            ('can_edit_' + modelo, 'Pode editar ' + modelo),
            ('can_delete_' + modelo, 'Pode deletar ' + modelo),
            ('can_view_' + modelo, 'Pode visualizar ' + modelo),
        ]

        for codename, nome in permissoes:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                name=nome,
                content_type=content_type,
            )
            if created:
                print(f"✅ Permissão '{nome}' criada com sucesso!")
            else:
                print(f"⚠️ Permissão '{nome}' já existe.")
