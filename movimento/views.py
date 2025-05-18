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


def excluir_movimentacao(request, id):
    movimentacao = get_object_or_404(Ativo, id=id)

    if request.method == "POST":
        movimentacao.delete()
        return redirect('listar_movimentacoes')

    return render(request, 'movimento/excluir.html', {'movimentacao': movimentacao})

def excluir_movimentacao_ativo(request, id):
    movimentacao_ativo = get_object_or_404(Ativo, id=id)

    if request.method == "POST":
        movimentacao_ativo.delete()
        return redirect('listar_movimentacoes_ativo')

    return render(request, 'movimento/movimento_ativo_excluir.html', {'movimentacao': movimentacao_ativo})



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
