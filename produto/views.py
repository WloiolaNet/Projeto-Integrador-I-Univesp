from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .models import Produto, CategoriaProduto,LocalizacaoProduto,DetalheTecnico,DetalheTecnicoValor
from .forms import ProdutoForm,LocalizacaoProdutoForm,CategoriaProdutoForm,FichaTecnicaProdutoForm,FichaTecnicaValorProdutoForm,ProdutoFiltroForm
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from historico.utils import registrar_historico
from saima.middleware import get_current_user
from django.utils import timezone
# No início do seu arquivo views.py
from historico.models import Historico
from datetime import datetime  # Importação do módulo datetime padrão
from django.db.models import Max
import re



def obter_icone_para(campo_nome):
    icones = {
        "Peso": "bi-weight",
        "Cor": "bi-palette",
        "Tensão": "bi-lightning",
        # adicione mais conforme necessário
    }
    return icones.get(campo_nome, "")



@login_required
@permission_required('produto.add_produto', raise_exception=True)
def criar_produto(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)  # Agora 'produto' está definido corretamente
            form.save()

            # Verifique se a função registrar_historico está sendo chamada corretamente
            print(f"Produto criado: {produto.nome}")  # Para verificar se o produto foi criado

            # Registrar histórico
            registrar_historico(
                modelo='Produto',
                objeto_id=produto.id,
                alterado_por=request.user,
                tipo_alteracao='CREATE',
                dados={
                    'nome': produto.nome,
                    'marca': produto.marca,
                    'modelo': produto.modelo,
                    'localizacao': produto.localizacao,
                    'categoria': produto.categoria,
                    'data_aquisicao': produto.data_aquisicao,
                    'preco': produto.preco,
                    'status': produto.status,
                    'condicao': produto.condicao,
                    'imagem': produto.imagem,
                    'fichatecnica': produto.fichatecnica,
                    'estoque_atual': produto.estoque_atual,
                }
            )

            return redirect('listar_produtos')  # Altere para a URL correta
        else:
            return JsonResponse({'error': 'Erro ao cadastrar produto.', 'details': form.errors}, status=400)
    else:
        form = ProdutoForm()
    return render(request, 'produto/produto_add.html', {'form': form})


@login_required
@permission_required('produto.add_produto', raise_exception=True)
def criar_produtos(request):
    fabricantes = ["Dell", "HP", "Samsung", "Apple", "Lenovo", "LG", "Asus"]

    if request.method == 'POST':
        # Inicializando os formulários com dados POST
        produto_form = ProdutoForm(request.POST, request.FILES)
        ficha_form = FichaTecnicaValorProdutoForm(request.POST)

        if produto_form.is_valid() and ficha_form.is_valid():
            # Salva o produto no banco de dados
            produto = produto_form.save()

            # Cria o detalhe técnico relacionado ao produto
            detalhe = ficha_form.save(commit=False)  # Não salva ainda
            detalhe.produto = produto  # Associa o produto ao detalhe técnico
            detalhe.save()  # Salva o detalhe técnico no banco

            # Associa o DetalheTecnicoValor ao campo fichatecnica do Produto
            produto.fichatecnica = detalhe
            produto.save()

            # Redireciona para a página de listagem de produtos
            return redirect('listar_produtos')  # Altere para a URL correta

        else:
            # Se os formulários não forem válidos, exibe as mensagens de erro
            return render(request, 'produto/produto_add.html', {
                'produto_form': produto_form, 
                'ficha_form': ficha_form, 
                'fabricantes': fabricantes
            })

    else:
        # Para requisição GET, inicializa os formulários vazios
        produto_form = ProdutoForm()
        ficha_form = FichaTecnicaValorProdutoForm()

    return render(request, 'produto/produto_add.html', {
        'produto_form': produto_form, 
        'ficha_form': ficha_form, 
        'fabricantes': fabricantes
    })


@login_required
@permission_required('produto.add_categoriaproduto', raise_exception=True)
def criar_categoria_produto(request):
    if request.method == "POST":
        form = CategoriaProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categoria_produto_listar')
    else:
        form = CategoriaProdutoForm()
    return render(request, 'produto/categoria_produto_criar.html', {'form': form})

@login_required
@permission_required('produto.add_localizacaoproduto', raise_exception=True)
def criar_localizacao_produto(request):
    if request.method == "POST":
        form = LocalizacaoProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('localizacao_produto_listar')
    else:
        form = LocalizacaoProdutoForm()
    return render(request, 'produto/localizacao_produto_criar.html', {'form': form})

@login_required
@permission_required('produto.add_detalhetecnico', raise_exception=True)
def criar_fichatecnica_produto(request):
    if request.method == "POST":
        form = FichaTecnicaProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('fichatecnica_produto_listar')
    else:
        form = FichaTecnicaProdutoForm()
    return render(request, 'produto/fichatecnica_produto_criar.html', {'form': form})



@login_required
@permission_required('produto.change_produto', raise_exception=True)
def editar_produto(request, id):
    produto = Produto.objects.get(id=id)  # Recupera o produto a ser editado
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            # Armazena o estado atual do produto antes da alteração
            produto_antigo = Produto.objects.get(id=id)
            
            # Salva o produto com as novas alterações
            produto_atualizado = form.save()

            # Verifica os campos que foram alterados
            campos_alterados = {}
            for campo in form.changed_data:
                campos_alterados[campo] = getattr(produto_atualizado, campo)

            # Registrar histórico
            registrar_historico(
                modelo='Produto',
                objeto_id=produto_atualizado.id,
                alterado_por=request.user,
                tipo_alteracao='UPDATE',
                dados={
                    'nome': produto.nome,
                    'marca': produto.marca,
                    'modelo': produto.modelo,
                    'localizacao': produto.localizacao,
                    'categoria': produto.categoria,
                    'data_aquisicao': produto.data_aquisicao,
                    'preco': produto.preco,
                    'status': produto.status,
                    'condicao': produto.condicao,
                    'imagem': produto.imagem,
                    'fichatecnica': produto.fichatecnica,
                    'estoque_atual': produto.estoque_atual,
                }
            )

            return redirect('listar_produtos')  # Redireciona para a lista de produtos
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'produto/produto_edit.html', {'form': form})



@login_required
@permission_required('produto.change_categoriaproduto', raise_exception=True)
def editar_categoria_produto(request, id):
    categoria = CategoriaProduto.objects.get(id=id)
    if request.method == "POST":
        form = CategoriaProdutoForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoria_produto_listar')
    else:
        form = CategoriaProdutoForm(instance=categoria)
    return render(request, 'produto/categoria_produto_editar.html', {'form': form})

@login_required
@permission_required('produto.change_localizacaoproduto', raise_exception=True)
def editar_localizacao_produto(request, id):
    produto = LocalizacaoProduto.objects.get(id=id)
    if request.method == "POST":
        form = LocalizacaoProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('localizacao_produto_listar')
    else:
        form = LocalizacaoProdutoForm(instance=produto)
    return render(request, 'produto/localizacao_produto_editar.html', {'form': form})

@login_required
@permission_required('produto.change_detalhetecnico', raise_exception=True)
def editar_fichatecnica_produto(request, id):
    produto = DetalheTecnico.objects.get(id=id)
    if request.method == "POST":
        form = FichaTecnicaProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('fichatecnica_produto_listar')
    else:
        form = FichaTecnicaProdutoForm(instance=produto)
    return render(request, 'produto/fichatecnica_produto_editar.html', {'form': form})


@login_required
@permission_required('produto.delete_produto', raise_exception=True)
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == "POST":
        produto.delete()
        return redirect('listar_produtos')

    return render(request, 'produto/excluir.html', {'produto': produto})

@login_required
@permission_required('produto.delete_categoriaproduto', raise_exception=True)
def excluir_categoria_produto(request, id):
    categoria = get_object_or_404(CategoriaProduto, id=id)

    if request.method == "POST":
        categoria.delete()
        return redirect('categoria_produto_listar')

    return render(request, 'produto/categoria_produto_excluir.html', {'categoria': categoria})

@login_required
@permission_required('produto.delete_localizacaoproduto', raise_exception=True)
def excluir_localizacao_produto(request, id):
    localizacao = get_object_or_404(LocalizacaoProduto, id=id)

    if request.method == "POST":
        localizacao.delete()
        return redirect('localizacao_produto_listar')

    return render(request, 'produto/localizacao_produto_excluir.html', {'localizacao': localizacao})


@login_required
@permission_required('produto.delete_detalhetecnico', raise_exception=True)
def excluir_fichatecnica_produto(request, id):
    fichatecnica = get_object_or_404(DetalheTecnico, id=id)

    if request.method == "POST":
        fichatecnica.delete()
        return redirect('fichatecnica_produto_listar')

    return render(request, 'produto/fichatecnica_produto_excluir.html', {'ficha tecnica': fichatecnica})


@login_required
@permission_required('produto.view_produto', raise_exception=True)
def listar_produtos(request):
    busca = request.GET.get('busca', '').strip()
    
    # Filtragem de produtos com base na busca
    if busca:
        produtos_lista = Produto.objects.filter(
            Q(nome__icontains=busca) |
            Q(marca__icontains=busca) |
            Q(modelo__icontains=busca) |
            Q(categoria__nome__icontains=busca)
        ).order_by('nome', 'marca', 'modelo')
    else:
        produtos_lista = Produto.objects.all().order_by('nome', 'marca', 'modelo')

    # Paginação
    paginator = Paginator(produtos_lista, 10)
    page = request.GET.get('page')
    produtos = paginator.get_page(page)

    # Registrar consulta no histórico
    alterado_por = get_current_user()  # Obtém o usuário atual que está acessando
    dados_consulta = {
        'busca': busca  # A busca realizada, caso exista
    }

    Historico.objects.create(
        modelo="Produto",  # Modelo que está sendo consultado
        objeto_id=0,    # Não há objeto específico sendo alterado
        alterado_por=alterado_por,
        tipo_alteracao='SEARCH',  # Tipo de alteração para indicar que é uma consulta
        data_alteracao=timezone.now(),
        dados=json.dumps(dados_consulta)  # Dados relacionados à consulta
    )

    # Contexto para a renderização da página
    context = {
        'produtos': produtos,
        'busca': busca
    }
    
    return render(request, 'produto/lista.html', context)




@login_required
@permission_required('produto.view_categoriaproduto', raise_exception=True)
def categoria_produto_listar(request):
    busca = request.GET.get('busca', '').strip()
    categorias  = CategoriaProduto.objects.all()
    
    if busca:
        categorias = categorias.annotate(
            nome_lower=Lower('nome')
        ).filter(nome_lower__contains=busca.lower())

    paginator = Paginator(categorias, 10)
    page = request.GET.get('page')
    categorias_paginadas = paginator.get_page(page)

    context = {
        'categorias': categorias_paginadas,           # para o select
        'busca': busca,
    }
    return render(request, 'produto/categoria_produto_listar.html', context)


@login_required
@permission_required('produto.view_localizacaoproduto', raise_exception=True)
def localizacao_produto_listar(request):
    busca = request.GET.get('busca', '').strip()
    localizacoes = LocalizacaoProduto.objects.all()

    if busca:
        localizacoes = localizacoes.annotate(
            nome_lower=Lower('nome')
        ).filter(nome_lower__contains=busca.lower())

    paginator = Paginator(localizacoes, 10)
    page = request.GET.get('page')
    localizacoes_paginadas = paginator.get_page(page)

    context = {
        'localizacoes': localizacoes_paginadas,
        'busca': busca,
    }
    return render(request, 'produto/localizacao_produto_listar.html', context)


@login_required
@permission_required('produto.view_detalhetecnico', raise_exception=True)
def fichatecnica_produto_listar(request):
    busca = request.GET.get('busca', '').strip()
    fichatecnicas = DetalheTecnico.objects.all()

    if busca:
        fichatecnicas = fichatecnicas.annotate(
            nome_lower=Lower('categoria__nome')
        ).filter(nome_lower__contains=busca.lower())

    paginator = Paginator(fichatecnicas, 10)
    page = request.GET.get('page')
    fichatecnica_paginadas = paginator.get_page(page)

    context = {
        'fichatecnicas': fichatecnica_paginadas,
        'busca': busca,
    }
    return render(request, 'produto/fichatecnica_produto_listar.html', context)


@login_required
@permission_required('produto.view_produto')
def consultar_produto(request, id):
    ativo = get_object_or_404(Produto, id=id)  
    return render(request, 'produto/consultar.html', {'ativo': ativo})

@login_required
@permission_required('produto.view_categoriaproduto')
def consultar_categoria_produto(request, id):
    ativo = get_object_or_404(CategoriaProduto, id=id)  
    return render(request, 'produto/categoria_produto_consultar.html', {'ativo': ativo})

@login_required
@permission_required('produto.view_localizacaoproduto')
def consultar_localizacao_produto(request, id):
    ativo = get_object_or_404(LocalizacaoProduto, id=id)  
    return render(request, 'produto/localizacao_produto_consultar.html', {'ativo': ativo})

@login_required
@permission_required('produto.view_fichatecnicaproduto')
def consultar_fichatecnica_produto(request, id):
    ativo = get_object_or_404(DetalheTecnico, id=id)  
    return render(request, 'produto/fichatecnica_produto_consultar.html', {'ativo': ativo})

def get_ficha_tecnica(request):
    if request.method == 'POST':
        categoria = request.POST.get('categoria', '')  # Categoria selecionada do combobox
        if categoria:
            detalhes = DetalheTecnico.objects.filter(categoria=categoria)
        else:
            detalhes = DetalheTecnico.objects.all()

        ficha_tecnica = []
        for detalhe in detalhes:
            ficha_tecnica.append({
                'categoria': detalhe.categoria.id if detalhe.categoria else None,  # Usando o id da categoria
                'nome': detalhe.titulo,
                'icon': detalhe.icone_bootstrap or '',
                'placeholder': detalhe.placeholder # Correção do campo correto

            })

        return JsonResponse(ficha_tecnica, safe=False)
    return JsonResponse({'error': 'Método inválido'}, status=405)



@login_required
@permission_required('produto.view_produto', raise_exception=True)
def relatorio_log_produtos(request):
    # Filtra os registros de log para o modelo "Produto"
    logs_produtos = Historico.objects.filter(modelo="Produto").order_by('-data_alteracao')
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
        logs_produtos = logs_produtos.filter(data_alteracao__gte=data_inicio)

    if data_fim:
        if hora_fim:
            # Se hora_fim for fornecida, combina com a data
            data_fim = datetime.strptime(data_fim + ' ' + hora_fim, '%Y-%m-%d %H:%M')
        else:
            # Caso contrário, usa apenas a data
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')

        # Torna a data "aware" se o fuso horário estiver ativado
        data_fim = timezone.make_aware(data_fim, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        logs_produtos = logs_produtos.filter(data_alteracao__lte=data_fim)
    elif data_inicio and data_fim:
        # Converte as strings para datetime e faz a conversão para timezone-aware
        data_inicio = datetime.strptime(data_inicio + ' ' + hora_inicio, '%Y-%m-%d %H:%M')
        data_fim = datetime.strptime(data_fim + ' ' + hora_fim, '%Y-%m-%d %H:%M')
        data_inicio = timezone.make_aware(data_inicio, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        data_fim = timezone.make_aware(data_fim, timezone.get_current_timezone())  # Torna a data consciente do fuso horário
        logs_produtos = logs_produtos.filter(data_alteracao__range=[data_inicio, data_fim])

    # Filtro de busca por nome do produto
    valor_busca = ''
    resultado_busca = request.GET.get('busca', None)
    if resultado_busca:
        valor_busca = resultado_busca.strip()
        if valor_busca:
            logs_produtos = logs_produtos.filter(nome_produto__icontains=valor_busca)

    # Filtros adicionais: tipo de alteração e alterado por
    alterado_por = request.GET.get('alterado_por', '')
    tipo_alteracao = request.GET.get('tipo_alteracao', '')

    if alterado_por:
        logs_produtos = logs_produtos.filter(alterado_por__username=alterado_por)
    if tipo_alteracao:
        logs_produtos = logs_produtos.filter(tipo_alteracao=tipo_alteracao)

    # Lista de usuários únicos para o select
    usuarios = Historico.objects.filter(modelo="Produto").values_list('alterado_por__username', flat=True).distinct()

 # Dicionário com traduções dos campos
    traducao_campos = {
        'codigo_produto': '<strong>Código Produto</strong>',
        'nome': '<strong>Descrição</strong>',
        'marca': '<strong>Marca</strong>',
        'modelo': '<strong>Modelo</strong>',
        'localizacao': '<strong>Localização</strong>',
        'categoria': '<strong>Categoria</strong>',
        'data_aquisicao': '<strong>Data Aquisição</strong>',
        'preco': '<strong>Preço</strong>',
        'status': '<strong>Status</strong>',
        'condicao' : '<strong>Estado Produto</strong>',
        'imagem' : '<strong>Caminho da Imagem</strong>',
        'fichatecnica' : '<strong>Ficha Tecnica</strong>',
        'estoque_atual' : '<strong>Estoque Atual</strong>',
        # Adicione mais conforme necessário
    }


    # Limpeza de dados (removendo aspas e chaves de campos JSON se for necessário)
    for log in logs_produtos:
        dados_alteracao = log.dados
        if isinstance(dados_alteracao, str):
            dados_alteracao = dados_alteracao.replace('"', '').replace('{', '').replace('}', '')
       

         # Traduz os campos
        for campo_en, campo_pt in traducao_campos.items():
            dados_alteracao = re.sub(rf'\b{campo_en}\b', campo_pt, dados_alteracao)        
         

        data_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:\+|-)\d{2}:\d{2}'



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
    paginator = Paginator(logs_produtos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto enviado ao template
    context = {
        'logs_produtos': page_obj,
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

    return render(request, 'produto/relatorio_log_produtos.html', context)


@login_required
@permission_required('produto.view_produto', raise_exception=True)
def relatorio_produtos(request):
    produtos = Produto.objects.all()
    form = ProdutoFiltroForm(request.GET or None)

    if form.is_valid():
        nome = form.cleaned_data.get('nome')
        categoria = form.cleaned_data.get('categoria')
        preco_min = form.cleaned_data.get('preco_min')
        preco_max = form.cleaned_data.get('preco_max')

        if nome:
            produtos = produtos.filter(nome__icontains=nome)
        if categoria:
            produtos = produtos.filter(categoria=categoria)
        if preco_min is not None:
            produtos = produtos.filter(preco__gte=preco_min)
        if preco_max is not None:
            produtos = produtos.filter(preco__lte=preco_max)

    paginator = Paginator(produtos, 10)
    page = request.GET.get('page')
    produtos_paginadas = paginator.get_page(page)


    context = {
        'form': form,
        'produtos': produtos_paginadas,
    }
    return render(request, 'produto/relatorio_produtos.html', context)


def obter_proxima_linha(request):
    categoria_id = request.GET.get('categoria_id')
    if categoria_id:
        registros = DetalheTecnico.objects.filter(categoria_id=categoria_id)
        if registros.exists():
            proxima_linha = registros.aggregate(Max('linha'))['linha__max'] + 1
        else:
            proxima_linha = 1
        return JsonResponse({'proxima_linha': proxima_linha})
    return JsonResponse({'erro': 'Categoria não fornecida'}, status=400)


