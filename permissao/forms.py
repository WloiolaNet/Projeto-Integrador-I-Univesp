from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class PermissaoForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'content_type','codename']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content_type'].queryset = ContentType.objects.all().order_by('model')
        self.fields['content_type'].label_from_instance = lambda obj: f"{obj.app_label} - {obj.model.capitalize()}"


        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Permissão'}),
            'content_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de objeto da Permissão'}),            
            'codename': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome interno da Permissão'}),
        }
