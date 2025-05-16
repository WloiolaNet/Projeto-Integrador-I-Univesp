from django import forms
from .models import Produto
from .models import CategoriaProduto
from .models import LocalizacaoProduto, DetalheTecnico, DetalheTecnicoValor



class ProdutoForm(forms.ModelForm):
    imagem = forms.ImageField(
        label="Escolher Nova Imagem",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'style': 'margin-top: 20px;'})
    )
    preco = forms.DecimalField(required=False, label='Preço',max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0'
        }))

    class Meta:
        model = Produto
        exclude = ['estoque_atual']  # Remova estoque_atual do form se não quiser que o usuário preencha
        fields = '__all__'
        labels = {
            'localizacao': 'Localização',
            'data_aquisicao': 'Data de aquisição',
            'condicao': 'Condição',
            'codigo_produto':'Código do Produto'
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantindo que a opção "Selecione" seja exibida no campo categoria
        if 'categoria' in self.fields:
            self.fields['categoria'].empty_label = "Selecione"
        # Garantindo que a opção "Selecione" seja exibida no campo categoria
        if 'localizacao' in self.fields:
            self.fields['localizacao'].empty_label = "Selecione"
        
                # Remove o checkbox "Clear"
        if 'imagem' in self.fields:
            self.fields['imagem'].widget.clear_checkbox_label = ''
            self.fields['imagem'].widget.template_name = 'widgets/custom_clearable_file_input.html'



class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = '__all__'
        labels = {
            'nome': 'Nome da Categoria',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da categoria'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'categoria' in self.fields:
            self.fields['categoria'].empty_label = "Selecione"

class LocalizacaoProdutoForm(forms.ModelForm):
    class Meta:
        model = LocalizacaoProduto
        fields = '__all__'
        labels = {
            'nome': 'Nome da Localizacao',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da localização'
            }),
        }

class FichaTecnicaProdutoForm(forms.ModelForm):
    class Meta:
        model = DetalheTecnico
        fields = '__all__'
        labels = {
            'categoria': 'Nome da Ficha Tecnica',  # Corrigido para o nome correto do campo
        }
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Escolha a categoria da ficha técnica'
            }),
            'linha': forms.NumberInput(attrs={  # Adicionado para o campo linha
                'class': 'form-control',
                'placeholder': 'Número da Linha'
            }),
            'titulo': forms.TextInput(attrs={  # Corrigido para o campo título
                'class': 'form-control',
                'placeholder': 'Título da Ficha Técnica'
            }),
        }    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantindo que a opção "Selecione" seja exibida no campo categoria
        if 'categoria' in self.fields:
            self.fields['categoria'].empty_label = "Selecione"


class FichaTecnicaValorProdutoForm(forms.ModelForm):
    class Meta:
        model = DetalheTecnicoValor
        fields = '__all__'
        labels = {
            'categoria': 'Nome da Ficha Técnica',
        }
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Escolha a Ficha Técnica'
            }),
            'linha': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número da Linha'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do Detalhe Técnico'
            }),
            'detalhe_tecnico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Detalhes do Produto'
            }),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
                # Garantindo que a opção "Selecione" seja exibida no campo categoria
            if 'categoria' in self.fields:
                self.fields['categoria'].empty_label = "Selecione"


class ProdutoFiltroForm(forms.Form):
    nome = forms.CharField(required=False, label='Nome do Produto')
    categoria = forms.ModelChoiceField(queryset=CategoriaProduto.objects.all(), required=False)
    preco_min = forms.DecimalField(required=False, label='Preço Mínimo',max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0'
        }))
    preco_max = forms.DecimalField(required=False, label='Preço Máximo',max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0'
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantindo que a opção "Selecione" seja exibida no campo categoria
        if 'categoria' in self.fields:
            self.fields['categoria'].empty_label = "Selecione"
