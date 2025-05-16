from django.contrib import admin
from .models import Produto, CategoriaProduto, LocalizacaoProduto, DetalheTecnico,DetalheTecnicoValor
from django.utils.html import format_html


class DetalheTecnicoValorInline(admin.TabularInline):
    model = DetalheTecnicoValor
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'modelo', 'categoria', 'localizacao', 'data_aquisicao', 'preco', 'status')
    search_fields = ('nome', 'marca', 'modelo')
    list_filter = ('categoria', 'localizacao', 'status')
    list_per_page = 25



class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class LocalizacaoProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class DetalheTecnicoAdmin(admin.ModelAdmin):
    list_display = ('categoria',)
    search_fields = ('categoria',)

class DetalheTecnicoValorAdmin(admin.ModelAdmin):
    list_display = ('produto', 'categoria', 'linha', 'titulo', 'detalhe_tecnico')
    list_filter = ('categoria', 'produto')
    search_fields = ('titulo', 'detalhe_tecnico', 'produto__nome', 'categoria__titulo')
    raw_id_fields = ('produto', 'categoria')



admin.site.register(Produto, ProdutoAdmin)
admin.site.register(CategoriaProduto, CategoriaProdutoAdmin)
admin.site.register(LocalizacaoProduto, LocalizacaoProdutoAdmin)
admin.site.register(DetalheTecnico, DetalheTecnicoAdmin)
admin.site.register(DetalheTecnicoValor, DetalheTecnicoValorAdmin)



   


