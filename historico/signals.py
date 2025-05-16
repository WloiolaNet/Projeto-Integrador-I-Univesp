from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Historico
from saima.middleware import get_current_user  # Certifique-se de que essa função retorna o usuário atual corretamente
import json
from datetime import datetime
import logging
from django.db import connection

logger = logging.getLogger(__name__)
User = get_user_model()


# Função para converter objetos não serializáveis como datetime
def default_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


# Função para capturar as consultas SQL
def capturar_consultas():
    # Lista todas as consultas SQL executadas
    consultas = []
    for query in connection.queries:
        consultas.append({
            'sql': query['sql'],
            'tempo_execucao': query['time']
        })
    return consultas


# Signal para salvar histórico de criação/atualização
@receiver(post_save)
def salvar_historico_criacao_atualizacao(sender, instance, created, **kwargs):
    if sender == Historico:
        return  # Ignorar alterações no próprio histórico

    tipo_alteracao = 'CREATE' if created else 'UPDATE'

    # Coleta os dados do objeto salvo
    try:
        dados = {
            field.name: getattr(instance, field.name, None)
            for field in instance._meta.fields
            if field.name != 'id'
        }
    except Exception as e:
        logger.error(f"Erro ao coletar dados da instância: {e}")
        dados = {"erro": str(e)}

    # Garantir que alterado_por seja corretamente atribuído
    alterado_por = getattr(instance, 'alterado_por', None)
    if not alterado_por:
        alterado_por = get_current_user()  # Certifique-se de que a função get_current_user() retorna o usuário correto

    # Captura as consultas SQL realizadas
    consultas = capturar_consultas()

    # Garantir que a instância tenha um ID antes de acessar
    objeto_id = getattr(instance, 'id', None)
    if objeto_id is None:
        logger.error("A instância não tem um ID definido")
        return

    # Cria o histórico
    Historico.objects.create(
        modelo=sender.__name__,
        objeto_id=objeto_id,
        alterado_por=alterado_por,
        tipo_alteracao=tipo_alteracao,
        data_alteracao=timezone.now(),
        dados=json.dumps(dados, default=default_converter),
        #consultas_json=json.dumps(consultas)  # Salvando as consultas no histórico, se necessário
    )


# Signal para salvar histórico de exclusão
@receiver(post_delete)
def salvar_historico_exclusao(sender, instance, **kwargs):
    if sender == Historico:
        return  # Ignorar exclusões no próprio histórico

    try:
        dados = {
            field.name: getattr(instance, field.name, None)
            for field in instance._meta.fields
            if field.name != 'id'
        }
    except Exception as e:
        logger.error(f"Erro ao coletar dados da instância (delete): {e}")
        dados = {"erro": str(e)}

    # Garantir que alterado_por seja corretamente atribuído
    alterado_por = getattr(instance, 'alterado_por', None)
    if not alterado_por:
        alterado_por = get_current_user()  # Certifique-se de que a função get_current_user() retorna o usuário correto

    # Captura as consultas SQL realizadas
    consultas = capturar_consultas()

    # Garantir que a instância tenha um ID antes de acessar
    objeto_id = getattr(instance, 'id', None)
    if objeto_id is None:
        logger.error("A instância não tem um ID definido")
        return

    # Cria o histórico
    Historico.objects.create(
        modelo=sender.__name__,
        objeto_id=objeto_id,
        alterado_por=alterado_por,
        tipo_alteracao='DELETE',
        data_alteracao=timezone.now(),
        dados=json.dumps(dados, default=default_converter),
        #consultas_json=json.dumps(consultas)  # Salvando as consultas no histórico, se necessário
    )


@receiver(post_save)
def salvar_historico_criacao_atualizacao(sender, instance, created, **kwargs):
    if sender == Historico:
        return  # Ignorar alterações no próprio histórico

    tipo_alteracao = 'CREATE' if created else 'UPDATE'
    logger.debug(f"Tipo de alteração: {tipo_alteracao} para {sender.__name__}, instância: {instance}")

    # Coleta os dados do objeto salvo
    try:
        dados = {
            field.name: getattr(instance, field.name, None)
            for field in instance._meta.fields
            if field.name != 'id'
        }
    except Exception as e:
        logger.error(f"Erro ao coletar dados da instância: {e}")
        dados = {"erro": str(e)}

    # Garantir que alterado_por seja corretamente atribuído
    alterado_por = getattr(instance, 'alterado_por', None)
    if not alterado_por:
        alterado_por = get_current_user()  # Certifique-se de que a função get_current_user() retorna o usuário correto

    # Captura as consultas SQL realizadas
    consultas = capturar_consultas()

    # Garantir que a instância tenha um ID antes de acessar
    objeto_id = getattr(instance, 'id', None)
    if objeto_id is None:
        logger.error("A instância não tem um ID definido")
        return

    # Cria o histórico
    Historico.objects.create(
        modelo=sender.__name__,
        objeto_id=objeto_id,
        alterado_por=alterado_por,
        tipo_alteracao=tipo_alteracao,
        data_alteracao=timezone.now(),
        dados=json.dumps(dados, default=default_converter),
        #consultas_json=json.dumps(consultas)  # Salvando as consultas no histórico, se necessário
    )
