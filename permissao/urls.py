from django.urls import path
from .views import listar_permissoes, criar_permissao, editar_permissao,excluir_permissao

urlpatterns = [
    path('', listar_permissoes, name='listar_permissoes'),
    path('permissao/criar/', criar_permissao, name='criar_permissao'),
    path('permissao/editar/<int:id>/', editar_permissao, name='editar_permissao'),
    path('permissao/excluir/<int:id>/', excluir_permissao, name='excluir_permissao'),
    
]
