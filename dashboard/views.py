from django.shortcuts import render
from docx import Document
from docx.shared import Inches
import os
from barcode import EAN13
from barcode.writer import ImageWriter
from django.http import HttpResponse
import shutil
import openpyxl
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
#from .models import produto
from django.db.models import Q
from django.shortcuts import render
from movimento.models import Ativo, MovimentacaoAtivo
from django.db.models import Count, Sum
from django.utils.timezone import now
from datetime import timedelta
import calendar
from django.db.models import F
from django.db.models import OuterRef, Subquery, Max

def dashboard_view(request):
    hoje = now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year
    mes_passado = (hoje.replace(day=1) - timedelta(days=1)).month
    ano_passado = ano_atual if mes_passado != 12 else ano_atual - 1

    total_ativos = Ativo.objects.count()
    
    entradas = MovimentacaoAtivo.objects.filter(status_novo='ativo', data__month=mes_atual, data__year=ano_atual).count()
    saidas = MovimentacaoAtivo.objects.filter(status_novo='em_uso', data__month=mes_atual, data__year=ano_atual).count()
    manutencao = MovimentacaoAtivo.objects.filter(status_novo='manutencao', data__month=mes_atual, data__year=ano_atual).count()

    entradas_passado = MovimentacaoAtivo.objects.filter(status_anterior='ativo', data__month=mes_passado, data__year=ano_passado).count()
    saidas_passado = MovimentacaoAtivo.objects.filter(status_anterior='em_uso', data__month=mes_passado, data__year=ano_passado).count()
    manutencao_passado = MovimentacaoAtivo.objects.filter(status_anterior='manutencao', data__month=mes_passado, data__year=ano_passado).count()

    ativos_mais_utilizados = Ativo.objects.annotate(
        total_movimentacoes=Count('movimentacaoativo')
    ).order_by('-total_movimentacoes')[:5]

    entradas_json = {"total": entradas}
    saidas_json = {"total": saidas}
    manutencao_json = {"total": manutencao}

    movimentacoes_por_categoria = MovimentacaoAtivo.objects \
        .select_related('ativo__codigo_produto__categoria') \
        .annotate(categoria_nome=F('ativo__codigo_produto__categoria__nome')) \
        .values('categoria_nome') \
        .annotate(movimentacoes=Count('id')) \
        .order_by('categoria_nome')

    movimentacoes_por_categoria_json = [
        {'nome': mov['categoria_nome'], 'total_movimentacoes': mov['movimentacoes']}
        for mov in movimentacoes_por_categoria
    ]

    # Tendência dos últimos 6 meses
    tendencia_json = {}
    for ativo in Ativo.objects.all():
        dados = []
        for i in range(5, -1, -1):
            data_ref = hoje - timedelta(days=30*i)
            mes = calendar.month_abbr[data_ref.month]
            count = MovimentacaoAtivo.objects.filter(
                ativo=ativo,
                data__month=data_ref.month,
                data__year=data_ref.year
            ).count()
            dados.append({'mes': mes, 'movimentacoes': count})
        tendencia_json[ativo.codigo_produto.nome] = dados

    # CORREÇÃO PRINCIPAL: ativos disponíveis (última movimentação = ativo)
    ultimas_movimentacoes = MovimentacaoAtivo.objects.filter(
        ativo=OuterRef('pk')
    ).order_by('-data')

    ativos_disponiveis = Ativo.objects.annotate(
        ultimo_status=Subquery(ultimas_movimentacoes.values('status_novo')[:1])
    ).filter(ultimo_status='ativo').count()

    context = {
        'total_ativos': total_ativos,
        'entradas': entradas,
        'saidas': saidas,
        'manutencao': manutencao,
        'entradas_passado': entradas_passado,
        'saidas_passado': saidas_passado,
        'manutencao_passado': manutencao_passado,
        'ativos_disponiveis': ativos_disponiveis,
        'ativos_mais_utilizados': ativos_mais_utilizados,
        'entradas_json': entradas_json,
        'saidas_json': saidas_json,
        'manutencao_json': manutencao_json,
        'tendencia_json': tendencia_json,
        'movimentacoes_por_categoria': movimentacoes_por_categoria_json,
    }

    return render(request, 'dashboard/dashboard_ativo.html', context)
