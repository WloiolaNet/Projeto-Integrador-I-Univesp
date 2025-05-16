# grupo/admin.py
from django.contrib import admin

# O modelo GrupoPersonalizado foi removido ou não está definido em models.py
# Por isso, comentamos a linha abaixo:
# from .models import GrupoPersonalizado

# Também comentamos o registro do modelo inexistente:
# @admin.register(GrupoPersonalizado)
# class InfoGrupoAdmin(admin.ModelAdmin):
#     list_display = ('grupo', 'descricao')
#     search_fields = ('grupo__name', 'descricao')
