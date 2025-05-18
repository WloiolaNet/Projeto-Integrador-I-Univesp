from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .forms import UsuarioForm,UsuarioFiltroForm
from django.contrib.auth import get_user_model
from .models import Usuario
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User  # Importando o modelo correto
from django.contrib import messages
from django.db.models import ProtectedError
from django.db import IntegrityError
from historico.models import Historico
from datetime import datetime  # Importação do módulo datetime padrão
from django.utils import timezone
import re


@login_required
@permission_required('usuario.add_usuario', raise_exception=True)
def criar_usuario(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuario/criar.html', {'form': form})

@login_required
@permission_required('usuario.change_usuario', raise_exception=True)
def editar_usuario(request, id):
    Usuario = get_user_model()
    usuario = Usuario.objects.get(id=id)
    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
           
            form.save()
            form.save_m2m()  # Salva grupos e outros relacionamentos ManyToMany

            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuario/editar.html', {'form': form})


@login_required
@permission_required('usuario.delete_usuario', raise_exception=True)
def excluir_usuario(request, id):
    usuario = Usuario.objects.filter(id=id).first()  # Evita erro 404

    if not usuario:
        return render(request, 'usuario/erro.html', {'mensagem': 'Usuário não encontrado.'})  # Página personalizada de erro

    if request.method == "POST":
        try:
            usuario.delete()
            messages.success(request, "✅ Usuário excluído com sucesso.")
        except (ProtectedError, IntegrityError):
            messages.error(request, "❌ Este usuário está vinculado a outros registros e não pode ser excluído.")
        return redirect('listar_usuarios')

    return render(request, 'usuario/excluir.html', {'usuario': usuario})




@login_required
@permission_required('usuario.view_usuario', raise_exception=True)
def listar_usuarios(request):
    busca = request.GET.get('busca', '').strip()
    if busca:
        usuarios_lista = Usuario.objects.annotate(
        first_name_lower=Lower('first_name'),
        last_name_lower=Lower('last_name'),
        username_lower=Lower('username')
        ).filter(username_lower__contains=busca.lower()).prefetch_related('groups')
    else:
        usuarios_lista = Usuario.objects.all().prefetch_related('groups')
    paginator = Paginator(usuarios_lista, 10)  # 10 por página
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)
    context = {
        'usuarios': usuarios,
        'busca': busca
    }
    return render(request, 'usuario/lista.html', context)

def erro_403(request, exception=None):
    return render(request, '403.html', status=403)


@login_required
@permission_required('usuario.view_usuario', raise_exception=True)
def relatorio_log_usuarios(request):
    # Filtra os registros de log para o modelo "usuario"
    logs_usuarios = Historico.objects.filter(modelo="Usuario").order_by('-data_alteracao')
    tipos_alteracao = Historico.objects.values_list('tipo_alteracao', flat=True).distinct()
    tipos_alteracao = sorted(set(tipos_alteracao))  # Garante ordenação e remove duplicados

    # Filtros de data e hora
    data_inicio = request.GET.get('data_inicio', None)
    hora_inicio = request.GET.get('hora_inicio', None)
    data_fim = request.GET.get('data_fim', None)
    hora_fim = request.GET.get('hora_fim', None)

    if data_inicio:
        if hora_inicio:
            # Se hora_inicio for fornecida, combina com a data
            data_inicio = datetime.strptime(data_inicio + ' ' + hora_inicio, '%Y-%m-%d %H:%M')
        else:
            # Caso contrário, usa apenas a data
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')

        # Torna a data "aware" se o fuso horário estiver ativado
        data_inicio = timezone.make_aware(data_inicio, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        logs_usuarios = logs_usuarios.filter(data_alteracao__gte=data_inicio)

    if data_fim:
        if hora_fim:
            # Se hora_fim for fornecida, combina com a data
            data_fim = datetime.strptime(data_fim + ' ' + hora_fim, '%Y-%m-%d %H:%M')
        else:
            # Caso contrário, usa apenas a data
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')

        # Torna a data "aware" se o fuso horário estiver ativado
        data_fim = timezone.make_aware(data_fim, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        logs_usuarios = logs_usuarios.filter(data_alteracao__lte=data_fim)
    elif data_inicio and data_fim:
        # Converte as strings para datetime e faz a conversão para timezone-aware
        data_inicio = datetime.strptime(data_inicio + ' ' + hora_inicio, '%Y-%m-%d %H:%M')
        data_fim = datetime.strptime(data_fim + ' ' + hora_fim, '%Y-%m-%d %H:%M')
        data_inicio = timezone.make_aware(data_inicio, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        data_fim = timezone.make_aware(data_fim, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        logs_usuarios = logs_usuarios.filter(data_alteracao__range=[data_inicio, data_fim])

    # Filtro de busca por nome do produto
    valor_busca = ''
    resultado_busca = request.GET.get('busca', None)
    if resultado_busca:
        valor_busca = resultado_busca.strip()
        if valor_busca:
            logs_usuarios = logs_usuarios.filter(nome_usuario__icontains=valor_busca)

    # Filtros adicionais: tipo de alteração e alterado por
    alterado_por = request.GET.get('alterado_por', '')
    tipo_alteracao = request.GET.get('tipo_alteracao', '')

    if alterado_por:
        logs_usuarios = logs_usuarios.filter(alterado_por__username=alterado_por)
    if tipo_alteracao:
        logs_usuarios = logs_usuarios.filter(tipo_alteracao=tipo_alteracao)

    # Lista de usuários únicos para o select
    usuarios = Historico.objects.filter(modelo="Produto").values_list('alterado_por__username', flat=True).distinct()


    # Dicionário com traduções dos campos
    traducao_campos = {
        'username': '<strong>Usuário</strong>',
        'last_login': '<strong>Último Acesso</strong>',
        'email': '<strong>E-mail</strong>',
        'is_superuser': '<strong>Super Usuário</strong>',
        'first_name': '<strong>Nome</strong>',
        'last_name': '<strong>Sobrenome</strong>',
        'is_staff': '<strong>Equipe</strong>',
        'is_active': '<strong>Ativo</strong>',
        'date_joined': '<strong>Data de Cadastro</strong>',
        'cargo' : '<strong>Cargo</strong>',
        # Adicione mais conforme necessário
    }
    # Limpeza de dados (removendo aspas e chaves de campos JSON se for necessário)
    if logs_usuarios.exists():  # Verifica se logs_usuarios não está vazio
        for log in logs_usuarios:
            dados_alteracao = log.dados
            if isinstance(dados_alteracao, str):
                dados_alteracao = dados_alteracao.replace('"', '').replace('{', '').replace('}', '')
                 # Remover a palavra "password" (ou outras palavras associadas à senha)
               # Expressão regular para remover 'password:' e o conteúdo até a vírgula
                dados_alteracao = re.sub(r'password:\s*[^,]*,', '', dados_alteracao)

                # Traduz os campos
                for campo_en, campo_pt in traducao_campos.items():
                    dados_alteracao = re.sub(rf'\b{campo_en}\b', campo_pt, dados_alteracao)
                
                # Expressões regulares para encontrar as datas
                data_pattern_1 = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+\d{2}:\d{2}'  # Com milissegundos
                data_pattern_2 = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}'  # Sem milissegundos

                # Combina as duas expressões regulares
                data_pattern = f'({data_pattern_1}|{data_pattern_2})'


                def formatar_data(match):
                        data_iso = match.group()
                        
                         # Remove a parte do fuso horário (se necessário) e converte a data para o formato desejado
                        data = datetime.fromisoformat(data_iso.split('+')[0])  # Remove o fuso horário para formatação
                        return data.strftime('%d/%m/%Y %H:%M:%S')  # Formato desejado

                    # Substitui as datas que atendem à condição (com milissegundos)
                dados_alteracao_formatado = re.sub(data_pattern, formatar_data, dados_alteracao)


            log.dados = dados_alteracao_formatado

   

    # Paginação: 15 itens por página
    paginator = Paginator(logs_usuarios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto enviado ao template
    context = {
        'logs_usuarios': page_obj,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
        'valor_busca': valor_busca,
        'alterado_por': alterado_por,
        'tipos_alteracao': tipos_alteracao,
        'tipo_alteracao': tipo_alteracao,
        'usuarios': usuarios,
    }

    return render(request, 'usuario/relatorio_log_usuarios.html', context)

def filtrar_informacoes_usuario(dados):
    # Remover ou ocultar informações sensíveis, como senha
    # Aqui você pode definir o que remover, como o campo 'password' por exemplo.
    if 'password' in dados:
        dados['password'] = '**oculto**'
    return dados


@login_required
@permission_required('usuario.view_usuario', raise_exception=True)
def relatorio_usuarios(request):
    usuarios = Usuario.objects.all()
    form = UsuarioFiltroForm(request.GET or None)

    if form.is_valid():
        username = form.cleaned_data.get('username')
        
        if username:
            usuarios = usuarios.filter(username__icontains=username)
        
    paginator = Paginator(usuarios, 10)
    page = request.GET.get('page')
    usuarios_paginadas = paginator.get_page(page)


    context = {
        'form': form,
        'usuarios': usuarios_paginadas,
    }
    return render(request, 'usuario/relatorio_usuarios.html', context)


