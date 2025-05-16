from django.urls import path
from .views import listar_grupos, criar_grupo, excluir_grupo, editar_grupo

urlpatterns = [
    path('', listar_grupos, name='listar_grupos'),
    path('grupo/criar/', criar_grupo, name='criar_grupo'),
    path('grupo/editar/<int:id>/', editar_grupo, name='editar_grupo'),
    path('grupo/excluir/<int:id>/', excluir_grupo, name='excluir_grupo'),
]
