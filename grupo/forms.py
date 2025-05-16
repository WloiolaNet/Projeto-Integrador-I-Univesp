from django import forms
from django.contrib.auth.models import Group, Permission

class GrupoForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'duallistbox'})
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Grupo'}),
        }
