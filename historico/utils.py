# historico/utils.py
from .models import Historico
import json
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def registrar_historico(modelo, objeto_id, alterado_por, tipo_alteracao, dados):
    logger.debug(f"Registrando histórico: Modelo={modelo}, Objeto ID={objeto_id}, Tipo Alteração={tipo_alteracao}")
    
    # Verifica e serializa o campo 'localizacao' se necessário
    if 'localizacao' in dados:
        localizacao = dados['localizacao']
        if hasattr(localizacao, 'nome'):  # Verifica se é um objeto com atributo 'nome'
            dados['localizacao'] = localizacao.nome  # Armazena o nome ou outro atributo adequado
    
    # Verifica e serializa o campo 'categoria' se necessário
    if 'categoria' in dados:
        categoria = dados['categoria']
        if hasattr(categoria, 'nome'):  # Verifica se é um objeto com atributo 'nome'
            dados['categoria'] = categoria.nome  # Armazena o nome ou outro atributo adequado
    
    # Log para verificar os dados antes de criar o histórico
    logger.debug(f"Dados do histórico a serem registrados: {dados}")
    
    try:
        # Cria o registro no histórico
        historico = Historico.objects.create(
            modelo=modelo,
            objeto_id=objeto_id,
            alterado_por=alterado_por,
            tipo_alteracao=tipo_alteracao,
            data_alteracao=timezone.now(),
            dados=json.dumps(dados)  # Serializa os dados para JSON
        )
        logger.debug(f"Histórico registrado com sucesso: {historico}")
    except Exception as e:
        logger.error(f"Erro ao registrar histórico: {e}")
