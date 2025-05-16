from django import forms
from .models import Ativo, Produto, LocalizacaoProduto,MovimentacaoAtivo
from django.db import models
from django.db.models import Q



class AtivoForm(forms.ModelForm):
    # Campo adicional de tipo de entrada
    TIPO_ENTRADA_CHOICES = [
        ('entrada', 'Entrada de Ativo'),
        # Adicione mais opções no futuro, se necessário
    ]
    tipo_entrada = forms.ChoiceField(
        choices=TIPO_ENTRADA_CHOICES,
        required=False,
        label="Tipo de Entrada",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Ativo
        fields = ['codigo_ativo', 'codigo_produto', 'imei', 'numero_serial', 'status_atual', 'localizacao', 'data_cadastro', 'tipo_entrada','categoria','quantidade','status_ativo']
        widgets = {
            'codigo_ativo': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_produto': forms.Select(attrs={'class': 'form-control'}),
            'imei': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serial': forms.TextInput(attrs={'class': 'form-control'}),
            'status_atual': forms.Select(attrs={'class': 'form-control'}),
            'status_ativo': forms.Select(attrs={'class': 'form-control'}),
            'localizacao': forms.Select(attrs={'class': 'form-control'}),
            'data_cadastro': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'quantidade',
                'min': '1',
                'step': '1'
            }),

        }

    # Ajuste do queryset para o campo localizacao
    def __init__(self, *args, **kwargs):
        super(AtivoForm, self).__init__(*args, **kwargs)
        self.fields['localizacao'].queryset = LocalizacaoProduto.objects.all()
        self.fields['imei'].required = False
        self.fields['numero_serial'].required = False
        self.fields['codigo_produto'].queryset = Produto.objects.all()
        self.fields['codigo_produto'].label_from_instance = lambda obj: f"{obj.codigo_produto}"
        
        if 'codigo_produto' in self.fields:
            self.fields['codigo_produto'].empty_label = "Selecione"
        if 'categoria' in self.fields:
            self.fields['categoria'].empty_label = "Selecione"
        if 'localizacao' in self.fields:
            self.fields['localizacao'].empty_label = "Selecione"
       
        if 'status_ativo' in self.fields:
            self.fields['status_ativo'].choices = [('', 'Selecione')] + list(Ativo.STATUS_ATIVO_CHOICES)

        if 'status_atual' in self.fields:
            self.fields['status_atual'].choices = [('', 'Selecione')] + list(Ativo.TIPO_CHOICES)


        if self.instance and self.instance.data_cadastro:
            self.initial['data_cadastro'] = self.instance.data_cadastro.strftime('%Y-%m-%d')

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Copia o valor de 'localizacao' para 'localizacao_atual_id'
        instance.localizacao_atual_id = self.cleaned_data.get('localizacao')
        
        if commit:
            instance.save()
        return instance




class MovimentacaoAtivoForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoAtivo
        fields = ['ativo', 'status_anterior', 'status_novo', 'local_anterior', 'local_novo', 'observacao', 'usuario_responsavel', 'data', 'usuario_final']
        widgets = {
            'ativo': forms.Select(attrs={'class': 'form-control'}),
            'status_anterior': forms.Select(attrs={'class': 'form-control'}),
            'status_novo': forms.Select(attrs={'class': 'form-control'}),
            'local_anterior': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Escolha a origem'}),
            'local_novo': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Escolha o destino'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control'}),
            'usuario_responsavel': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'usuario_final': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MovimentacaoAtivoForm, self).__init__(*args, **kwargs)
        
        if self.instance and self.instance.data:
            self.initial['data'] = self.instance.data.strftime('%Y-%m-%d')

        if self.instance.pk and self.instance.ativo:
            self.fields['local_anterior'].initial = self.instance.ativo.localizacao_atual.nome
        else:
            self.fields['local_anterior'].initial = "Localização não definida"
        
        self.fields['status_anterior'].choices = [('', 'Selecione')] + list(dict(MovimentacaoAtivo.TIPO_CHOICES).items())
        self.fields['status_novo'].choices = [('', 'Selecione')] + list(dict(MovimentacaoAtivo.TIPO_CHOICES).items())
        
        if 'usuario_responsavel' in self.fields:
            self.fields['usuario_responsavel'].empty_label = "Selecione"
        if 'local_anterior' in self.fields:
            self.fields['local_anterior'].empty_label = "Selecione"
        if 'local_novo' in self.fields:
            self.fields['local_novo'].empty_label = "Selecione"
        if 'ativo' in self.fields:
            self.fields['ativo'].empty_label = "Selecione"
        
        if 'ativo' in self.data:
            try:
                ativo_id = int(self.data.get('ativo'))
                ultimo = MovimentacaoAtivo.objects.filter(ativo_id=ativo_id).order_by('-data').first()
                status_atual = ultimo.status_novo if ultimo else Ativo.objects.get(id=ativo_id).status_atual

                self.fields['status_novo'].choices = [
                    (code, label) for code, label in MovimentacaoAtivo.TIPO_CHOICES if code != status_atual
                ]

                # Preenche o campo de usuário final com o último valor registrado (se existir)
                if ultimo:
                    self.fields['usuario_final'].initial = ultimo.usuario_final
            except Exception as e:
                print(f"Erro ao carregar a movimentação: {e}")

        # Verifique se o queryset está correto para o campo ativo
        if self.instance.pk and self.instance.ativo:
            try:
                self.fields['ativo'].queryset = Ativo.objects.filter(
                    models.Q(id=self.instance.ativo.id) | models.Q(status_atual=True)
                )
                # Assegure que o campo 'ativo' tem o valor inicial correto
                self.fields['ativo'].initial = self.instance.ativo
            except Ativo.DoesNotExist:
                print("Erro: Ativo não encontrado!")
        
    def clean_status_novo(self):
        status_novo = self.cleaned_data['status_novo']
        if status_novo not in dict(MovimentacaoAtivo.TIPO_CHOICES).keys():
            raise forms.ValidationError('Status inválido!')
        return status_novo


    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Copia o valor de 'localizacao' para 'localizacao_atual_id'
        instance.localizacao_atual_id = self.cleaned_data.get('localizacao_atual')
        
        if commit:
            instance.save()
        return instance
