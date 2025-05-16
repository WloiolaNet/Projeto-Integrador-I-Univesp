from django.contrib import admin
from .models import Ativo, MovimentacaoAtivo, CategoriaProduto, LocalizacaoProduto

# Registro do modelo Ativo
class AtivoAdmin(admin.ModelAdmin):
    list_display = ( 'imei', 'numero_serial', 'status_atual', 'localizacao', 'data_cadastro','status_ativo')
    search_fields = ('produto__codigo_produto', 'imei', 'numero_serial', 'status_atual','status_ativo')
    list_filter = ('status_atual', 'status_ativo','localizacao')
    ordering = ('-data_cadastro',)

# Registro do modelo MovimentacaoAtivo
class MovimentacaoAtivoAdmin(admin.ModelAdmin):
    list_display = ('ativo', 'status_anterior','status_novo', 'local_anterior', 'local_novo', 'data', 'usuario_responsavel','data')
    search_fields = ('ativo__produto__codigo_produto', 'status_anterior','status_novo', 'local_anterior', 'local_novo', 'usuario_responsavel__username')
    list_filter = ('status_anterior','status_novo', 'data', 'usuario_responsavel')
    ordering = ('-data',)

# Registro dos modelos no admin
admin.site.register(Ativo, AtivoAdmin)
admin.site.register(MovimentacaoAtivo, MovimentacaoAtivoAdmin)

