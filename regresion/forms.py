from django import forms
from core.models import Molde, Maquinaria

class PrediccionConsumoForm(forms.Form):
    molde = forms.ModelChoiceField(queryset=Molde.objects.all())
    maquina = forms.ModelChoiceField(queryset=Maquinaria.objects.all())
    horas_trabajadas = forms.FloatField(min_value=0)
    piezas_producidas = forms.IntegerField(min_value=0)
    precio_kwh = forms.FloatField(min_value=0)
