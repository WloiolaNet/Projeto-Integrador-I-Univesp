from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from PIL import Image



CONDICAO_CHOICES = [
    ('novo', 'Novo'),
    ('usado', 'Usado'),
    ('descartado', 'Descartado')
]

STATUS_CHOICES =[
('ativo','Ativo'),
('inativo', 'Inativo')
]

class LocalizacaoProduto(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


def validate_image(image):
    # Verifica extensão
    if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError('O arquivo deve ser uma imagem PNG, JPG ou JPEG.')
    
    # Verifica se é uma imagem de verdade
    try:
        # Isso forçará a leitura da imagem e levantará erro se ela for inválida
        img = Image.open(image)
        img.verify()
    except Exception:
        raise ValidationError('O arquivo enviado não é uma imagem válida.')
    
def validate_image_size(image):
    # Define o tamanho máximo do arquivo em bytes (exemplo: 5 MB)
    max_size = 5 * 1024 * 1024  # 5 MB
    if image.size > max_size:
        raise ValidationError('O arquivo da imagem não pode exceder 5 MB.')



class Produto(models.Model):
    codigo_produto = models.CharField(max_length=20, blank=True, null=True)
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    localizacao = models.ForeignKey(LocalizacaoProduto, on_delete=models.SET_NULL, null=True, blank=True)
    categoria = models.ForeignKey(CategoriaProduto,on_delete=models.SET_NULL, null=True, blank=True)
    data_aquisicao = models.DateField(default=timezone.now)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')
    condicao = models.CharField(max_length=20, choices=CONDICAO_CHOICES, default='ativo')
    imagem = models.ImageField(upload_to='produto/imagens/', blank=True, null=True, validators=[validate_image, validate_image_size])
    fichatecnica = models.ForeignKey('DetalheTecnicoValor',related_name='fichatecnicas',on_delete=models.SET_NULL, null=True, blank=True)
    estoque_atual = models.PositiveIntegerField(default=0)  # NOVO CAMPO


    def __str__(self):
        #return f"{self.codigo_produto} - {self.nome} {self.marca} {self.modelo}"
        return f"{self.codigo_produto}"


    class Meta:
        permissions = [
            ("pode_adicionar_ativo", "Pode adicionar ativo"),
            ("pode_modificar_ativo", "Pode modificar ativo"),
            ("pode_deletar_ativo", "Pode deletar ativo"),
            ("pode_visualizar_ativo", "Pode visualizar ativo"),
        ]

class DetalheTecnico(models.Model):
    categoria = models.ForeignKey(CategoriaProduto,related_name='detalhes_tecnicos', on_delete=models.SET_NULL, null=True, blank=True)
    linha = models.PositiveIntegerField(default=0)  # Adicionei aqui o campo linha
    titulo = models.CharField(max_length=100)
    icone_bootstrap = models.CharField(max_length=100, blank=True, null=True)
    placeholder = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.titulo

class DetalheTecnicoValor(models.Model):
    produto = models.ForeignKey(Produto, related_name='detalhe_tecnico', on_delete=models.CASCADE)
    categoria = models.ForeignKey(Produto,related_name='detalhes_categoria', on_delete=models.SET_NULL, null=True, blank=True)
    linha = models.PositiveIntegerField(default=0)  # Adicionei aqui o campo linha
    titulo = models.CharField(max_length=100)
    icone_bootstrap = models.CharField(max_length=100, blank=True, null=True)
    detalhe_tecnico = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'detalhe_tecnico_valor' 

    def __str__(self):
        return f"{self.titulo}: {self.detalhe_tecnico}"