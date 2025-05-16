from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_produtos, name='listar_produtos'),
    path('criar/', views.criar_produto, name='criar_produto'),
    path('editar/<int:id>/', views.editar_produto, name='editar_produto'),
    path('excluir/<int:id>/', views.excluir_produto, name='excluir_produto'),
    path('consultar/', views.listar_produtos, name='listar_produtos'),
    path('relatorio/log-produtos/', views.relatorio_log_produtos, name='relatorio_log_produtos'),
    path('relatorio/produtos/', views.relatorio_produtos, name='relatorio_produtos'),
    path('ajax/obter-proxima-linha/', views.obter_proxima_linha, name='obter_proxima_linha'),





    path('categoria-produto/', views.categoria_produto_listar, name='categoria_produto_listar'),
    path('categoria-produto/criar/', views.criar_categoria_produto, name='criar_categoria_produto'),
    path('categoria-produto/editar/<int:id>/', views.editar_categoria_produto, name='editar_categoria_produto'),
    path('categoria-produto/excluir/<int:id>/', views.excluir_categoria_produto, name='excluir_categoria_produto'),
    

    path('localizacao-produto/', views.localizacao_produto_listar, name='localizacao_produto_listar'),
    path('localizacao-produto/criar/', views.criar_localizacao_produto, name='criar_localizacao_produto'),
    path('localizacao-produto/editar/<int:id>/', views.editar_localizacao_produto, name='editar_localizacao_produto'),
    path('localizacao-produto/excluir/<int:id>/', views.excluir_localizacao_produto, name='excluir_localizacao_produto'),

    path('fichatecnica-produto/', views.fichatecnica_produto_listar, name='fichatecnica_produto_listar'),
    path('fichatecnica-produto/criar/', views.criar_fichatecnica_produto, name='criar_fichatecnica_produto'),
    path('fichatecnica-produto/editar/<int:id>/', views.editar_fichatecnica_produto, name='editar_fichatecnica_produto'),
    path('fichatecnica-produto/excluir/<int:id>/', views.excluir_fichatecnica_produto, name='excluir_fichatecnica_produto'),
    path('get_ficha_tecnica/', views.get_ficha_tecnica, name='get_ficha_tecnica'),




]
