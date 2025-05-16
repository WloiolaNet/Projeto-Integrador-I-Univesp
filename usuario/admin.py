from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    model = Usuario

    # Corrigido: remover campo many-to-many direto do list_display
    list_display = (
        'username', 'first_name', 'last_name', 'email',
        'cargo', 'mostrar_grupos', 'is_staff', 'is_active', 'date_joined'
    )

    list_filter = ('is_staff', 'is_active', 'cargo', 'groups')

    # Corrigido: remover duplicidade do campo 'groups'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Dados Profissionais', {'fields': ('cargo',)}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 'email',
                'cargo', 'groups', 'password1', 'password2', 'is_staff', 'is_active',
            ),
        }),
    )

    # Corrigido: remover campo many-to-many direto do search_fields
    search_fields = ('username', 'email', 'first_name', 'last_name', 'cargo')
    ordering = ('username',)

    # Método auxiliar para mostrar grupos no list_display
    def mostrar_grupos(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    mostrar_grupos.short_description = 'Grupos'

admin.site.register(Usuario, UsuarioAdmin)

