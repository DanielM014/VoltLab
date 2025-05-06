from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import CustomUser

class EditarUsuarioForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label="Rol")

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active']

class CambiarRolUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'is_staff']
        labels = {
            'is_staff': 'Rol (marcar para Administrador)',
        }

class CrearUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    nuevo_rol = forms.CharField(required=False, label="Nuevo Rol")
    grupo_existente = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Seleccionar Rol existente"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']