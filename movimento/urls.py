# urls.py (do app "produto" ou similar)
from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.listar_movimentacoes, name='listar_movimentacoes'),
    path('criar/', views.criar_movimentacao, name='criar_movimentacao'),
    path('editar/<int:id>/', views.editar_movimentacao, name='editar_movimentacao'),
    path('excluir/<int:id>/', views.excluir_movimentacao, name='excluir_movimentacao'),
    path('consultar/', views.listar_movimentacoes, name='listar_movimentacoes'),
    path('buscar-ativos/', views.buscar_ativos, name='buscar_ativos'),
    path('obter-localizacao/', views.obter_localizacao_ativo, name='obter_localizacao_ativo'),
    path('produto-autocomplete/',views.ProdutoAutocomplete.as_view(), name='produto-autocomplete'),
    path('get-nome-produto/', views.get_nome_produto, name='get_nome_produto'),
    path('buscar-localizacao/', views.buscar_localizacao, name='buscar_localizacao'),

    path('criar_movimentacao_ativo/', views.criar_movimentacao_ativo, name='criar_movimentacao_ativo'),
    path('editar_movimentacao_ativo/<int:id>/', views.editar_movimentacao_ativo, name='editar_movimentacao_ativo'),
    path('excluir_movimentacao_ativo/<int:id>/', views.excluir_movimentacao_ativo, name='excluir_movimentacao_ativo'),
    path('consultar_movimentacao_ativo/', views.listar_movimentacoes_ativo, name='listar_movimentacoes_ativo'),
    path('get-dados-produto/', views.get_dados_produto_por_ativo, name='get_dados_produto'),
    path('relatorio/movimentacoes/', views.relatorio_movimentacao_view, name='relatorio_movimentacao_view'),
    path('relatorio/log-movimentacao/', views.relatorio_log_movimentacao, name='relatorio_log_movimentacao'),
    
    
]
