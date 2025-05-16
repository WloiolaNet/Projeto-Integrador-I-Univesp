from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('criar/', views.criar_usuario, name='criar_usuario'),
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('excluir/<int:id>/', views.excluir_usuario, name='excluir_usuario'),
    path('relatorio/log-usuarios/', views.relatorio_log_usuarios, name='relatorio_log_usuarios'),
    path('relatorio/usuarios/', views.relatorio_usuarios, name='relatorio_usuarios'),
]
