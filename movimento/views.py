from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, MovimentacaoAtivo,LocalizacaoProduto,Ativo
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dal import autocomplete
from django.db import models
from django.core.paginator import Paginator
from django.shortcuts import render
from .forms import AtivoForm,MovimentacaoAtivoForm
from django.db.models import Q
from usuario.models import Usuario  # Certifique-se de importar o modelo correto
from django.utils import timezone
from .models import Ativo
from django.db import transaction
from .models import MovimentacaoAtivo
import logging
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()
from .filters import MovimentacaoAtivoFilter
from datetime import datetime, time
from django.template.loader import get_template
from django.http import HttpResponse
import tempfile
from historico.models import Historico
from datetime import datetime  # Importação do módulo datetime padrão
from django.utils import timezone
import re



def listar_movimentacoes(request):
    busca = request.GET.get('busca', '')
    movimentacoes = Ativo.objects.select_related('codigo_produto', 'localizacao')

    if busca:
        movimentacoes = movimentacoes.filter(
            Q(codigo_ativo__icontains=busca) |
            Q(imei__icontains=busca) |
            Q(numero_serial__icontains=busca) |
            Q(codigo_produto__nome__icontains=busca)
        )

    paginator = Paginator(movimentacoes.order_by('-data_cadastro'), 10)
    page = request.GET.get('page')
    movimentacoes_paginadas = paginator.get_page(page)

    return render(request, 'movimento/lista.html', {
        'movimentacoes': movimentacoes_paginadas,
        'busca': busca,
    })


def listar_movimentacoes_ativo(request):
    busca = request.GET.get('busca', '')
    movimentacoes = MovimentacaoAtivo.objects.select_related('ativo')

    if busca:
        movimentacoes = movimentacoes.filter(
            Q(ativo__icontains=busca) |
            Q(tipo__icontains=busca)             
        )

    paginator = Paginator(movimentacoes.order_by('-data'), 10)
    page = request.GET.get('page')
    movimentacoes_paginadas = paginator.get_page(page)

    return render(request, 'movimento/movimento_ativo_listar.html', {
        'movimentacoes': movimentacoes_paginadas,
        'busca': busca,
    })


@login_required
def obter_localizacao_ativo(request):
    produto_id = request.GET.get('produto_id')
    if produto_id:
        try:
            produto = Produto.objects.get(id=produto_id)
            localizacao = produto.localizacao.nome if produto.localizacao else '' # certifique-se de que é isso mesmo
            return JsonResponse({'localizacao': localizacao})
        except Produto.DoesNotExist:
            return JsonResponse({'localizacao': ''})
    return JsonResponse({'localizacao': ''})


@csrf_exempt
def buscar_localizacao(request):
    if request.method == 'POST':
        produto_id = request.POST.get('id')
        try:
            produto = Produto.objects.get(id=produto_id)
            return JsonResponse({'localizacao': produto.localizacao.nome})
        except Produto.DoesNotExist:
            return JsonResponse({'localizacao': 'Não encontrada'})

@login_required
def criar_movimentacao_view(request):
    produtos = Produto.objects.all()
    return render(request, 'criar.html', {'produtos': produtos})


    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Produto.objects.order_by('-id').first()
            if ultimo and ultimo.codigo:
                try:
                    ultimo_numero = int(ultimo.codigo.replace('ATV-', ''))
                except ValueError:
                    ultimo_numero = 0
            else:
                ultimo_numero = 0
            self.codigo = f"ATV-{ultimo_numero + 1:05d}"  # Ex: ATV-00001
        super().save(*args, **kwargs)



@login_required
def criar_movimentacao(request):
    if request.method == "POST":
        form = AtivoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Retorna JSON para o AJAX
            #return redirect('listar_movimentacoes') 
            return JsonResponse({'status': 'success', 'message': 'Movimentação salva com sucesso!'})
            
        else:
            # Retorna os erros do formulário
            return JsonResponse({'status': 'error', 'message': 'Verifique os dados.', 'errors': form.errors}, status=400)

    # Se não for POST, renderiza o formulário normalmente
    form = AtivoForm()
    return render(request, 'movimento/criar.html', {'form': form})



@login_required                                   
def registrar_movimentacao_logica_old(ativo, status_novo, local_anterior, local_novo, observacao, usuario_responsavel, usuario_final):
    print(f"local_novo: {local_novo}")

    # Garantir que usuario_responsavel seja uma instância do modelo Usuario
    if not isinstance(usuario_responsavel, Usuario):
        try:
            usuario_responsavel = Usuario.objects.get(username=usuario_responsavel)
        except Usuario.DoesNotExist:
            raise ValueError("Usuário responsável não encontrado.")
    
    # Se local_novo não for uma instância, tenta buscar por ID
    if not isinstance(local_novo, LocalizacaoProduto):
        try:
            local_novo = LocalizacaoProduto.objects.get(id=local_novo)
        except LocalizacaoProduto.DoesNotExist:
            raise ValueError(f"Localização nova com ID '{local_novo}' não encontrada.")
    
    local_anterior = ativo.localizacao_atual  # Agora você pega diretamente do ativo
    if isinstance(local_anterior, str):
        try:
            local_anterior = LocalizacaoProduto.objects.get(nome=local_anterior)
        except LocalizacaoProduto.DoesNotExist:
            raise ValueError(f"Localização anterior '{local_anterior}' não encontrada.")

    # Pega a última movimentação para recuperar status anterior
    ultima_movimentacao = MovimentacaoAtivo.objects.filter(ativo=ativo).order_by('-data').first()

    

    movimentacao = MovimentacaoAtivo(
        ativo=ativo,
        status_anterior=ultima_movimentacao.status_novo if ultima_movimentacao else ativo.status_atual,
        status_novo=status_novo,
        local_anterior=local_anterior.nome if local_anterior else '',  # Grava o nome da localização anterior
        local_novo=local_novo,
        usuario_inicio=ativo.usuario_atual,
        usuario_final=str(usuario_final),
        usuario_responsavel=usuario_responsavel,
        observacao=observacao,
        data=timezone.now()
    )

    try:
        movimentacao.save()
    except Exception as e:
        raise ValueError(f"Erro ao salvar movimentação: {str(e)}")


logger = logging.getLogger(__name__)
def registrar_movimentacao_logica(ativo, status_novo, local_anterior, local_novo, observacao, usuario_responsavel, usuario_final):
    logger.debug(f"local_novo: {local_novo}")

    # Garantir que usuario_responsavel seja uma instância do modelo Usuario
    if not isinstance(usuario_responsavel, Usuario):
        try:
            usuario_responsavel = Usuario.objects.get(username=usuario_responsavel)
        except Usuario.DoesNotExist:
            raise ValueError("Usuário responsável não encontrado.")
    
    # Se local_novo não for uma instância, tenta buscar por ID
    if not isinstance(local_novo, LocalizacaoProduto):
        try:
            local_novo = LocalizacaoProduto.objects.get(id=local_novo)
        except LocalizacaoProduto.DoesNotExist:
            raise ValueError(f"Localização nova com ID '{local_novo}' não encontrada.")
    
    # Pega a localização anterior do ativo
    local_anterior = ativo.localizacao_atual  
    if isinstance(local_anterior, str):
        try:
            local_anterior = LocalizacaoProduto.objects.get(nome=local_anterior)
        except LocalizacaoProduto.DoesNotExist:
            raise ValueError(f"Localização anterior '{local_anterior}' não encontrada.")

    # Pega a última movimentação para recuperar status anterior
    ultima_movimentacao = MovimentacaoAtivo.objects.filter(ativo=ativo).order_by('-data').first()

    # Inicia a transação atômica
    try:
        with transaction.atomic():
        
            movimentacao = MovimentacaoAtivo(
                ativo=ativo,
                status_anterior=ultima_movimentacao.status_novo if ultima_movimentacao else ativo.status_atual,
                status_novo=status_novo,
                local_anterior=local_anterior if local_anterior else '',
                local_novo=local_novo,
                usuario_inicio=ativo.usuario_atual,
                usuario_final=str(usuario_final),
                usuario_responsavel=usuario_responsavel,
                observacao=observacao,
                data=timezone.now()
            )

            movimentacao.save()
            logger.info(f"Movimentação salva para o ativo: {ativo.id}")

            # Atualiza o campo de localizacao_atual diretamente
            # Atualiza o campo de localizacao_atual diretamente
            # Atualiza o campo de localizacao_atual diretamente
            # Atualiza o campo de localizacao_atual diretamente
            if ativo:
                if isinstance(local_novo, LocalizacaoProduto):
                    # Acessando o nome da localização e convertendo para string, caso necessário
                    Ativo.objects.filter(id=ativo.id).update(localizacao_atual=local_novo)
                    Ativo.objects.filter(id=ativo.id).update(status_atual=status_novo)


                    logger.info(f"Localização atualizada para: {ativo.localizacao_atual}")
                else:
                    raise ValueError("local_novo não é uma instância de LocalizacaoProduto.")
            else:
                raise ValueError("Ativo não encontrado ou inválido.")

    except Exception as e:
        logger.error(f"Erro ao salvar movimentação: {str(e)}")
        raise ValueError(f"Erro ao salvar movimentação: {str(e)}")

@login_required
def criar_movimentacao_ativo(request):
    if request.method == "POST":
        form = MovimentacaoAtivoForm(request.POST)
        if form.is_valid():
            ativo = form.cleaned_data['ativo']
            novo_status = form.cleaned_data['status_novo']
            local_anterior = form.cleaned_data['local_anterior']
            local_novo = form.cleaned_data['local_novo']
            observacao = form.cleaned_data.get('observacao', "")
            usuario_responsavel = request.user  # já é uma instância de Usuario
            usuario_final = form.cleaned_data['usuario_final']

            # Registra a movimentação
            registrar_movimentacao_logica(
                ativo, novo_status,
                local_anterior, local_novo,
                observacao, usuario_responsavel,
                usuario_final
            )

            return redirect('listar_movimentacoes_ativo')
    else:
        form = MovimentacaoAtivoForm(initial={'usuario_responsavel': request.user})

    return render(request, 'movimento/movimento_ativo_criar.html', {'form': form})


@login_required
def get_dados_produto_por_ativo(request):
    ativo_id = request.GET.get('ativo_id')

    try:
        ativo = Ativo.objects.select_related('codigo_produto', 'categoria', 'localizacao', 'localizacao_atual').get(id=ativo_id)
        produto = ativo.codigo_produto  # Relacionamento com Produto

        # Verifica a categoria do ativo para definir o IMEI ou número serial
        if ativo.categoria and ativo.categoria.nome.lower() == 'celular':
            imei_serial = ativo.imei if ativo.imei else 'N/A'
        else:
            imei_serial = ativo.numero_serial if ativo.numero_serial else 'N/A'

        data = {
            'codigo_produto': produto.codigo_produto,
            'nome': produto.nome,
            'imei': ativo.imei if ativo.imei else 'N/A',
            'numero_serial': ativo.numero_serial if ativo.numero_serial else 'N/A',
            'categoria': ativo.categoria.nome if ativo.categoria else 'N/A',
            'status_atual': ativo.status_atual,
            'localizacao': {
                'id': ativo.localizacao.id if ativo.localizacao else None,
                'nome': ativo.localizacao.nome if ativo.localizacao else None,
            },
            'localizacao_atual': {
                'id': ativo.localizacao_atual.id if ativo.localizacao_atual else None,
                'nome': ativo.localizacao_atual.nome if ativo.localizacao_atual else None,
            },
        }

        return JsonResponse(data)

    except Ativo.DoesNotExist:
        return JsonResponse({'error': f'Ativo com id {ativo_id} não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def editar_movimentacao(request, id):
    # Obtém a instância do Ativo que será editado
    movimentacao = get_object_or_404(Ativo, pk=id)

    # Verifica se o método da requisição é POST
    if request.method == "POST":
        # Passa a instância do ativo para o formulário
        form = AtivoForm(request.POST, instance=movimentacao)
        
        # Se o formulário for válido, salva a instância
        if form.is_valid():
            form.save()
            return redirect('listar_movimentacoes')  # Redireciona para a lista de movimentações
    else:
        # Se não for POST, preenche o formulário com a instância
        form = AtivoForm(instance=movimentacao)

    # Renderiza o template com o formulário
    return render(request, 'movimento/editar.html', {'form': form})

@login_required
def editar_movimentacao_ativo(request, id):
    try:
        movimentacao_ativo = MovimentacaoAtivo.objects.get(id=id)
    except MovimentacaoAtivo.DoesNotExist:
        # Trate o caso de a movimentação não ser encontrada, se necessário
        return redirect('listar_movimentacoes_ativo')

    if request.method == "POST":
        form = MovimentacaoAtivoForm(request.POST, request.FILES, instance=movimentacao_ativo)
        if form.is_valid():
            form.save()
            return redirect('listar_movimentacoes_ativo')
        else:
            # Se o formulário não for válido, faça algo aqui, como adicionar mensagens de erro
            print(form.errors)  # Apenas para depuração
    else:
        form = MovimentacaoAtivoForm(instance=movimentacao_ativo)

    return render(request, 'movimento/movimento_ativo_editar.html', {'form': form})

@login_required
def excluir_movimentacao(request, id):
    movimentacao = get_object_or_404(Ativo, id=id)

    if request.method == "POST":
        movimentacao.delete()
        return redirect('listar_movimentacoes')

    return render(request, 'movimento/excluir.html', {'movimentacao': movimentacao})

@login_required
def excluir_movimentacao_ativo(request, id):
    movimentacao_ativo = get_object_or_404(Ativo, id=id)

    if request.method == "POST":
        movimentacao_ativo.delete()
        return redirect('listar_movimentacoes_ativo')

    return render(request, 'movimento/movimento_ativo_excluir.html', {'movimentacao': movimentacao_ativo})


@login_required
def buscar_ativos(request):
    term = request.GET.get('term', '')
    
    # Filtra os produtos associados às movimentações que contêm o termo buscado no nome
    produtos = Produto.objects.filter(nome__icontains=term)[:20]
    
    # Construa o resultado com o id, nome do produto e outros dados desejados
    results = [{'id': p.id, 'text': p.nome} for p in produtos]
    
    return JsonResponse({'results': results})


class ProdutoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Produto.objects.none()

        qs = Produto.objects.all()

        if self.q:
            qs = qs.filter(
                models.Q(codigo_produto__icontains=self.q)|
                models.Q(nome__icontains=self.q)
                )

        return qs


@login_required
def get_nome_produto(request):
    # Verifique se o 'id' foi passado como parâmetro na URL
    produto_id = request.GET.get('id')

    if not produto_id:
        return JsonResponse({'error': 'ID do produto não fornecido'}, status=400)

    try:
        # Busque o produto com status 'ativo'
        produto = Produto.objects.get(id=produto_id, status='ativo')
        return JsonResponse({'nome': produto.nome})

    except Produto.DoesNotExist:
        # Produto não encontrado ou status não é 'ativo'
        return JsonResponse({'error': 'Produto não encontrado ou não está ativo'}, status=404)

    except Exception as e:
        # Captura qualquer outra exceção e retorna um erro genérico
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required
def relatorio_movimentacao_view(request):
    # Copia os parâmetros GET para poder modificar
    data = request.GET.copy()
    
    # Converter data__gte (Data Inicial) de dd/mm/yyyy para yyyy-mm-dd
    data_gte = data.get('data__gte')
    if data_gte:
        try:
            dt = datetime.strptime(data_gte, '%d/%m/%Y')
            data['data__gte'] = dt.date().isoformat()
        except ValueError:
            pass  # Pode colocar um log ou mensagem se quiser
    
    # Converter data__lte (Data Final) de dd/mm/yyyy para yyyy-mm-dd + 23:59:59
    data_lte = data.get('data__lte')
    if data_lte:
        try:
            dt = datetime.strptime(data_lte, '%d/%m/%Y')
            dt = datetime.combine(dt.date(), time.max)  # final do dia
            data['data__lte'] = dt.isoformat()
        except ValueError:
            pass
    
    filtro = MovimentacaoAtivoFilter(data, queryset=MovimentacaoAtivo.objects.select_related('ativo', 'local_anterior', 'local_novo'))
    return render(request, 'movimento/relatorio_movimentacao.html', {'filter': filtro, 'request': request})



@login_required
@permission_required('movimento.view_movimento', raise_exception=True)
def relatorio_log_movimentacao(request):
    # Filtra os registros de log para o modelo "usuario"
    logs_usuarios = Historico.objects.filter(modelo="MovimentacaoAtivo").order_by('-data_alteracao')
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
        'ativo': '<strong>Código do Ativo</strong>',
        'data': '<strong>Data da Alteração</strong>',
        'status_anterior': '<strong>Status Anterior</strong>',
        'status_novo': '<strong>Status Novo</strong>',
        'local_anterior': '<strong>Local Anterior</strong>',
        'local_novo': '<strong>Local Atual</strong>',
        'usuario_responsavel': '<strong>Usuário responsavel</strong>',
        'usuario_inicio': '<strong>Usuário Anterior</strong>',
        'usuario_final': '<strong>Usuário Atual</strong>',
        'observacao' : '<strong>Observação</strong>',
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
                          
                        # Converte direto para datetime aware (com timezone)
                        data_aware = datetime.fromisoformat(data_iso)
                        
                        # Converte para horário local
                        data_local = timezone.localtime(data_aware)
                        
                        return data_local.strftime('%d/%m/%Y %H:%M:%S')

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

    return render(request, 'movimento/relatorio_log_movimentacao.html', context)

def filtrar_informacoes_movimento(dados):
    # Remover ou ocultar informações sensíveis, como senha
    # Aqui você pode definir o que remover, como o campo 'password' por exemplo.
    if 'password' in dados:
        dados['password'] = '**oculto**'
    return dados