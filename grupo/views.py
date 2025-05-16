from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from .forms import GrupoForm
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseNotAllowed
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Value



@login_required
@permission_required('auth.view_group', raise_exception=True)
def listar_grupos(request):
    busca = request.GET.get('busca', '').strip()

    if busca:
        grupos_lista = Group.objects.annotate(
            name_lower=Lower('name'),
           
        ).filter(
            Q(name_lower__icontains=busca.lower())  
           
        )
    else:
        grupos_lista = Group.objects.all()

    paginator = Paginator(grupos_lista, 10)
    page = request.GET.get('page')
    grupos = paginator.get_page(page)

    return render(request, 'grupo/lista.html', {
        'grupos': grupos,
        'busca': busca
    })



@login_required
@permission_required('auth.add_group', raise_exception=True)
def criar_grupo(request):
    if request.method == "POST":
        form = GrupoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_grupos')
    else:
        form = GrupoForm()
    return render(request, 'grupo/criar.html', {'form': form})

@login_required
@permission_required('auth.change_group', raise_exception=True)
def editar_grupo(request, id):
    grupo = get_object_or_404(Group, id=id)

    if request.method == "POST":
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect("listar_grupos")  # Substitua pelo namespace correto, se necessário
    elif request.method == "GET":
        form = GrupoForm(instance=grupo)
    else:
        return HttpResponseNotAllowed(["GET", "POST"])  # Bloqueia outros métodos HTTP

    return render(request, "grupo/editar.html", {"form": form, "grupo": grupo})


@login_required
@permission_required('auth.delete_group', raise_exception=True)
def excluir_grupo(request, id):
    grupo = Group.objects.filter(id=id).first()  # Evita erro 404

    if not grupo:
        return render(request, 'grupo/erro.html', {'mensagem': 'Grupo não encontrado.'})  # Página personalizada de erro

    if request.method == "POST":
        grupo.delete()
        return redirect('listar_grupos')

    return render(request, 'grupo/excluir.html', {'grupo': grupo})


