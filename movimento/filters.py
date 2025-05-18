from django_filters import FilterSet, DateFilter, TypedChoiceFilter, ModelChoiceFilter, CharFilter
from django.forms import Select, DateInput
from .models import MovimentacaoAtivo, Ativo, LocalizacaoProduto
from django_filters import DateTimeFilter
from django.forms import DateTimeInput
from django.contrib.auth import get_user_model

User = get_user_model()



class MovimentacaoAtivoFilter(FilterSet):
    data__gte = DateTimeFilter(
        field_name='data',
        lookup_expr='gte',
        label='Data Inicial',
        widget=DateTimeInput(attrs={'type': 'date'})  # ou datetime-local para hora
    )
    data__lte = DateTimeFilter(
        field_name='data',
        lookup_expr='lte',
        label='Data Final',
        widget=DateTimeInput(attrs={'type': 'date'})
    )

    status_anterior = TypedChoiceFilter(
        choices=[('', 'Selecione')] + list(MovimentacaoAtivo.TIPO_CHOICES),
        widget=Select(),
        label='Status Anterior'
    )

    status_novo = TypedChoiceFilter(
        choices=[('', 'Selecione')] + list(MovimentacaoAtivo.TIPO_CHOICES),
        widget=Select(),
        label='Status Novo'
    )
    
    local_anterior = ModelChoiceFilter(
    field_name='local_anterior',
    queryset=LocalizacaoProduto.objects.all(),
    label='Local Anterior',
    empty_label='Selecione'
    )

    local_novo = ModelChoiceFilter(
        field_name='local_novo',
        queryset=LocalizacaoProduto.objects.all(),
        label='Local Novo',
        empty_label='Selecione'
    )

    usuario_responsavel = ModelChoiceFilter(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        label='Usuário Responsável',
        empty_label='Selecione'
    )


    ativo__codigo_ativo = CharFilter(lookup_expr='icontains', label='Código Ativo')
    ativo__imei = CharFilter(lookup_expr='icontains', label='IMEI')
    ativo__numero_serial = CharFilter(lookup_expr='icontains', label='Número Serial')

    class Meta:
        model = MovimentacaoAtivo
        fields = [
            'data__gte', 'data__lte', 'status_anterior', 'status_novo',
            'local_anterior', 'local_novo', 'usuario_responsavel',
            'ativo__codigo_ativo', 'ativo__imei', 'ativo__numero_serial'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['usuario_responsavel'].queryset = User.objects.filter(is_active=True).order_by('username')
