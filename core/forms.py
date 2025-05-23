from django import forms
from .models import Maquinaria, Molde, RegistroConsumo, MoldeMaquinariaAsignacion, PrecioEnergia, MesActivo
from django.db.models import Sum
from django.core.exceptions import ValidationError
from datetime import date
from datetime import datetime


class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = ['nombre', 'potencia_watts', 'voltaje', 'corriente']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['voltaje'].required = False
        self.fields['corriente'].required = False

    def clean(self):
        cleaned_data = super().clean()
        potencia_watts = cleaned_data.get('potencia_watts')
        voltaje = cleaned_data.get('voltaje')
        corriente = cleaned_data.get('corriente')

        # Caso 1: Si ya ingresaron potencia, todo bien
        if potencia_watts:
            return cleaned_data

        if not potencia_watts and voltaje and corriente:
            cleaned_data['potencia_watts'] = voltaje * corriente

        return cleaned_data
    



class MoldeForm(forms.ModelForm):
    class Meta:
        model = Molde
        fields = ['nombre', 'piezas_necesarias']

class RegistroConsumoForm(forms.ModelForm):
    class Meta:
        model = RegistroConsumo
        fields = [
            'molde',
            'maquina',
            'horas_trabajadas',
            'piezas_producidas',
            'fecha',
            'fecha_hipotetica_finalizacion',
            'precio_kwh_mes',
            'operario'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'fecha_hipotetica_finalizacion': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        molde = cleaned_data.get('molde')
        maquina = cleaned_data.get('maquina')
        piezas = cleaned_data.get('piezas_producidas')

        if molde and maquina:
            try:
                asignacion = MoldeMaquinariaAsignacion.objects.get(molde=molde, maquina=maquina)
            except MoldeMaquinariaAsignacion.DoesNotExist:
                raise ValidationError(f"La máquina seleccionada no está asignada al molde '{molde}'.")
            
            if piezas is not None and piezas > asignacion.piezas_asignadas:
                raise ValidationError(
                    f"No puedes registrar más de {asignacion.piezas_asignadas} piezas para esta máquina."
                )

        return cleaned_data

class FiltroDashboardForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    molde = forms.ModelChoiceField(
        queryset=Molde.objects.all(),
        required=False,
        empty_label="Todos los moldes"
    )

    
class AsignacionForm(forms.ModelForm):
    class Meta:
        model = MoldeMaquinariaAsignacion
        fields = '__all__'


    def clean(self):
        cleaned_data = super().clean()
        molde = cleaned_data.get('molde')
        piezas_nuevas = cleaned_data.get('piezas_asignadas')

        if molde and piezas_nuevas is not None:
            total_asignado = MoldeMaquinariaAsignacion.objects.filter(molde=molde).exclude(pk=self.instance.pk).aggregate(
                total=Sum('piezas_asignadas'))['total'] or 0
            piezas_restantes = molde.piezas_necesarias - total_asignado

            if piezas_nuevas > piezas_restantes:
                raise forms.ValidationError(
                    f"Solo puedes asignar hasta {piezas_restantes} piezas. Ya se han asignado {total_asignado} de {molde.piezas_necesarias}.")

        return cleaned_data
    
class PrecioEnergiaForm(forms.ModelForm):
    class Meta:
        model = PrecioEnergia
        fields = ['valor_kwh']

    def clean(self):
        cleaned_data = super().clean()
        valor_kwh = cleaned_data.get('valor_kwh')

        # Obtener el mes activo
        from .models import MesActivo  # importa aquí para evitar errores circulares
        mes_activo = MesActivo.objects.filter(activo=True).first()
        if not mes_activo:
            raise forms.ValidationError("No hay un mes activo definido.")

        fecha_mes = datetime(mes_activo.año, mes_activo.mes, 1)

        # Verifica si ya existe un registro en ese mes, excepto si es el mismo objeto en edición
        existe = PrecioEnergia.objects.filter(fecha_registro=fecha_mes)
        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            raise forms.ValidationError("Ya existe un precio registrado para este mes.")

        return cleaned_data
    

class SimuladorROIForm(forms.Form):
    maquina = forms.ModelChoiceField(queryset=Maquinaria.objects.all())
    porcentaje_ahorro = forms.ChoiceField(
        choices=[(0.2, '20%'), (0.3, '30%')],
        label="Ahorro energético estimado"
    )
    costo_inversion = forms.FloatField(label="Costo de la inversión (COP)")


class MesActivoForm(forms.ModelForm):
    class Meta:
        model = MesActivo
        fields = ['año', 'mes']  # Solo se permite seleccionar el mes activo
        widgets = {
            'mes': forms.Select(attrs={'class': 'form-control'})
        }