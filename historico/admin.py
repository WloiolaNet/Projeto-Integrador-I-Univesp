# admin.py
from django.contrib import admin
from .models import Historico

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'objeto_id', 'alterado_por', 'tipo_alteracao', 'data_alteracao')
    search_fields = ('modelo', 'objeto_id', 'alterado_por')
    list_filter = ('tipo_alteracao', 'data_alteracao')
