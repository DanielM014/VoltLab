from django import forms

class InversionForm(forms.Form):
    inversion = forms.FloatField(
        label="Valor de la inversión (COP)",
        min_value=10000,
        initial=100000,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
