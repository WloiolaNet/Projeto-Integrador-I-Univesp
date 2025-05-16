from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

Usuario = get_user_model()

class UsuarioForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']
