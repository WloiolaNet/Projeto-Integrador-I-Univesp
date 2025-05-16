# historico/models.py
from django.db import models
from django.conf import settings  # Correto para projetos com AUTH_USER_MODEL
from django.utils import timezone

class Historico(models.Model):
    modelo = models.CharField(max_length=255)
    objeto_id = models.PositiveIntegerField()
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Corrige o erro
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tipo_alteracao = models.CharField(max_length=50, choices=[
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('SEARCH', 'Consulta'),  # Adiciona o tipo de alteração 'Consulta'

    ])
    data_alteracao = models.DateTimeField(auto_now_add=True)
    dados = models.JSONField()
    #consultas_json = models.TextField(blank=True, null=True)  # Campo adicionado para consultas SQL


    def __str__(self):
        return f"{self.modelo} ({self.objeto_id}) - {self.tipo_alteracao} - {self.data_alteracao}"
