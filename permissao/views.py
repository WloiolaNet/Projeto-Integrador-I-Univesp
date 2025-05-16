from django.shortcuts import render, redirect
from django.contrib.auth.models import Permission
from .forms import PermissaoForm
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Value


from django.contrib.auth.models import Permission
from django.db.models import Q
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

@login_required
@permission_required('auth.view_permission', raise_exception=True)
def listar_permissoes(request):
    busca = request.GET.get('busca', '').strip()

    if busca:
        permissoes_lista = Permission.objects.annotate(
            name_lower=Lower('name'),
            content_type_model=Lower('content_type__model')
        ).filter(
            Q(name_lower__icontains=busca.lower()) |
            Q(content_type_model__icontains=busca.lower())
        )
    else:
        permissoes_lista = Permission.objects.all()

    paginator = Paginator(permissoes_lista, 10)
    page = request.GET.get('page')
    permissao = paginator.get_page(page)

    context = {
        'permissoes': permissao,
        'busca': busca
    }
    return render(request, 'permissao/lista.html', context)



@login_required
@permission_required('auth.add_permission', raise_exception=True)
def criar_permissao(request):
    if request.method == "POST":
        form = PermissaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_permissoes')
    else:
        form = PermissaoForm()
    return render(request, 'permissao/criar.html', {'form': form})

@login_required
@permission_required('auth.change_permission', raise_exception=True)
def editar_permissao(request, id):
    permissao = Permission.objects.get(id=id)
    if request.method == "POST":
        form = PermissaoForm(request.POST, instance=permissao)
        if form.is_valid():
            form.save()
            return redirect('listar_permissoes')
    else:
        form = PermissaoForm(instance=permissao)
    return render(request, 'permissao/editar.html', {'form': form})


@login_required
@permission_required('permissao.delete_permission', raise_exception=True)
def excluir_permissao(request, id):
    permissao = Permission.objects.filter(id=id).first()  # Evita erro 404

    if not permissao:
        return render(request, 'Permissao/erro.html', {'mensagem': 'Permissao não encontrado.'})  # Página personalizada de erro

    if request.method == "POST":
        permissao.delete()
        return redirect('listar_permissoes')

    return render(request, 'permissao/excluir.html', {'permissao': permissao})

