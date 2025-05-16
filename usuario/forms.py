from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password
from .models import Usuario  # Importa o modelo correto

class UsuarioForm(forms.ModelForm):
    username = forms.CharField(
        label="Nome de usuário",
        max_length=150,
        help_text="<br><small style='color: gray;'>Obrigatório. Máximo de 150 caracteres. Apenas letras, números e @/./+/-/_.</small>"
    )

    # Torne os campos de senha opcionais na edição:
    password1 = forms.CharField(
        widget=forms.PasswordInput(),
        label="Senha",
        required=False
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(),
        label="Confirmação de Senha",
        required=False
    )

    is_staff = forms.BooleanField(
        required=False,
        label="Administrador",
        help_text="<br><small style='color: gray;'>Indica se o usuário pode acessar o site administrativo.</small>"
    )

    is_active = forms.BooleanField(
        required=False,
        label="Conta ativa",
        help_text="<br><small style='color: gray;'>Indica se a conta do usuário está ativa.</small>"
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'duallistbox'}),
        label="Grupo(s)",
        required=False
    )

    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'duallistbox'}),
        label="Permissões específicas",
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'password1', 'password2',
            'first_name', 'last_name', 'email', 'cargo',
            'groups', 'user_permissions',
            'is_staff', 'is_active'
        ]
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'cargo': 'Cargo',
            'groups': 'Grupo(s)',
            'user_permissions': 'Permissões específicas'
        }
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'duallistbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        # Se algum dos campos for preenchido, as senhas devem coincidir
        if (password1 or password2) and password1 != password2:
            self.add_error('password2', "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        """ Sobrescreve o método save() para atualizar a senha somente se preenchida """
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.password = make_password(password1)  # Criptografa a nova senha
        if commit:
            user.save()
            self.save_m2m()  # Salva os relacionamentos many-to-many (groups e user_permissions)
        return user
    
class UsuarioFiltroForm(forms.Form):
    username = forms.CharField(required=False, label='Nome do Usuario')
    

    

