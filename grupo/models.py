from django import forms
from django.contrib.auth.models import Group, Permission

class GroupForm(forms.ModelForm):
    descricao = forms.CharField(required=False, widget=forms.Textarea)  # opcional, se quiser adicionar

    class Meta:
        model = Group
        fields = ['name', 'permissions']  # 'permissions' é o campo padrão
        widgets = {
            'permissions': forms.SelectMultiple(attrs={'class': 'duallistbox'})
        }

    
