from django.db import models
from django.utils import timezone
from produto.models import Produto, CategoriaProduto, LocalizacaoProduto  # Certifique-se de que esses modelos existam
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings

TIPO_ENTRADA_CHOICES = [
        ('entrada', 'Entrada de Ativo'),
    ]

class Ativo(models.Model):
    TIPO_CHOICES = [
        ('ativo', 'Disponível'),
        ('em_uso', 'Alocado'),
        ('manutencao', 'Em Manutenção'),
        ('baixado', 'Baixado'), 
    ]
    STATUS_ATIVO_CHOICES =[
        ('ativo','Ativo'),
        ('inativo','Inativo'),
    ]

    codigo_ativo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    codigo_produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='ativos_por_codigo')
    quantidade = models.IntegerField(verbose_name="Quantidade")
    imei = models.CharField(max_length=50,unique=True, blank=True, null=True)
    numero_serial = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status_atual = models.CharField(max_length=20,choices=TIPO_CHOICES,blank=True, null=True)
    status_ativo = models.CharField(max_length=20,choices=STATUS_ATIVO_CHOICES,blank=True, null=True)
    categoria = models.ForeignKey('produto.CategoriaProduto',on_delete=models.PROTECT)
    localizacao = models.ForeignKey('produto.LocalizacaoProduto', on_delete=models.PROTECT)  # Usando string
    localizacao_atual = models.ForeignKey('produto.LocalizacaoProduto', on_delete=models.PROTECT,blank=True, null=True,related_name='localizacao_atual')
    data_cadastro = models.DateTimeField(verbose_name="Data de Cadastro", blank=True, null=True)
    tipo_entrada = models.CharField(max_length=20, choices=TIPO_ENTRADA_CHOICES, default='entrada', blank=True, null=True)
    usuario_atual=models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return f"{self.codigo_ativo} "
    
    def save(self, *args, **kwargs):
        if self.localizacao:
            self.localizacao_atual = self.localizacao
        super().save(*args, **kwargs)

class MovimentacaoAtivo(models.Model):
    TIPO_CHOICES = [
        ('ativo', 'Disponível'),
        ('em_uso', 'Alocado'),
        ('manutencao', 'Em Manutenção'),
        ('baixado', 'Baixado'), 
    ]

    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    data = models.DateTimeField(verbose_name="Data de Cadastro", blank=True, null=True)  
    status_anterior = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status_novo = models.CharField(max_length=20, choices=TIPO_CHOICES)   
    local_anterior = models.ForeignKey('produto.LocalizacaoProduto', on_delete=models.PROTECT,related_name='movimentacoes_origem') 
    local_novo = models.ForeignKey('produto.LocalizacaoProduto', on_delete=models.PROTECT,related_name='movimentacoes_destino') 
    usuario_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    usuario_inicio = models.CharField(max_length=100, null=True, blank=True)
    usuario_final = models.CharField(max_length=100)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        data_formatada = self.data.strftime('%d/%m/%Y') if self.data else "Data não definida"
        return f"Movimentação de {self.ativo.codigo_produto} em {data_formatada}"
