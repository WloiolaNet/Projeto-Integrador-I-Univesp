from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render
from usuario.models import Usuario





from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.db import IntegrityError
from usuario.models import Usuario  # Importando o modelo correto
from django.contrib.auth.forms import UserCreationForm

def signup(request):
    if request.method == 'GET':
        return render(request, 'usuario_auth/signup.html', {
            'form': UserCreationForm()
        })

    else:
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'usuario_auth/signup.html', {
                'form': UserCreationForm(),
                "error": "As senhas não correspondem!"
            })

        try:
            # Criando usuário no modelo correto
            user = Usuario.objects.create_user(username=username, password=password1)
            user.save()

            login(request, user)  # Faz o login automático
            return redirect('dashboard_view')  # Redireciona para a home

        except IntegrityError:
            return render(request, 'usuario_auth/signup.html', {
                'form': UserCreationForm(),
                "error": "O nome de usuário já existe!"
            })


def login_view(request):
    if request.method =='GET':
        return render(request, 'usuario_auth/login.html',{
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request,'usuario_auth/login.html',{
                'form': AuthenticationForm,
                'error': 'Nome de usuário ou senha estão incorretos!'
            })
        else:
            login(request,user)
            return redirect('dashboard_view')
        

def recuperar_senha(request):
    return render(request, 'usuario_auth/recuperar_senha.html')

def password_reset_form(request):
    form = PasswordResetForm()

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="password_reset_email.html"
            )
            return render(request, "password_reset_done.html")  # Página de confirmação

    return render(request, "password_reset_form.html", {"form": form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')


def signout(request):
    logout(request)
    return redirect('home')



