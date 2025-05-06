from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from .models import Maquinaria, Molde, RegistroConsumo, PrecioEnergia, MesActivo
from .forms import MaquinariaForm, MoldeForm, RegistroConsumoForm, MoldeMaquinariaAsignacion, AsignacionForm, FiltroDashboardForm, PrecioEnergiaForm, SimuladorROIForm, MesActivoForm
from django.contrib.auth.mixins import LoginRequiredMixin
import plotly.graph_objs as go
from django.contrib.auth.mixins import UserPassesTestMixin
from collections import defaultdict
from django.db.models import Sum
from django.shortcuts import redirect
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from datetime import datetime
from django.http import JsonResponse
from collections import defaultdict



@login_required
def home(request):
    return render(request, 'core/home.html')

#/             Crud de la Maquinaria              #/
class MaquinariaListView(LoginRequiredMixin, ListView):
    model = Maquinaria
    template_name = 'core/maquinaria_list.html'
    context_object_name = 'maquinas'


class MaquinariaCreateView(LoginRequiredMixin, CreateView):
    model = Maquinaria
    form_class = MaquinariaForm
    template_name = 'core/maquinaria_form.html'
    success_url = reverse_lazy('maquinaria-list')


class MaquinariaUpdateView(LoginRequiredMixin, UpdateView):
    model = Maquinaria
    form_class = MaquinariaForm
    template_name = 'core/maquinaria_form.html'
    success_url = reverse_lazy('maquinaria-list')


class MaquinariaDeleteView(LoginRequiredMixin, DeleteView):
    model = Maquinaria
    template_name = 'core/maquinaria_confirm_delete.html'
    success_url = reverse_lazy('maquinaria-list')



#/          Crud de los moldes                  #/

class MoldeListView(LoginRequiredMixin, ListView):
    model = Molde
    template_name = 'core/molde_list.html'
    context_object_name = 'moldes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        asignaciones_por_molde = {}

        for molde in context['moldes']:
            asignaciones = molde.asignaciones.select_related('maquina').all()
            asignaciones_por_molde[molde.id] = asignaciones

        context['asignaciones_por_molde'] = asignaciones_por_molde
        return context


class MoldeCreateView(LoginRequiredMixin, CreateView):
    model = Molde
    form_class = MoldeForm
    template_name = 'core/molde_form.html'
    success_url = reverse_lazy('molde-list')


class MoldeUpdateView(LoginRequiredMixin, UpdateView):
    model = Molde
    form_class = MoldeForm
    template_name = 'core/molde_form.html'
    success_url = reverse_lazy('molde-list')


class MoldeDeleteView(LoginRequiredMixin, DeleteView):
    model = Molde
    template_name = 'core/molde_confirm_delete.html'
    success_url = reverse_lazy('molde-list')



#/      CRUD de la tabla final          #/


class RegistroConsumoListView(LoginRequiredMixin, ListView):
    model = RegistroConsumo
    template_name = 'core/consumo_list.html'
    context_object_name = 'registros'

    def get_queryset(self):
        queryset = super().get_queryset()
        mes_activo = MesActivo.objects.filter(activo=True).first()
        if mes_activo:
            return queryset.filter(
                fecha__year=mes_activo.año,
                fecha__month=mes_activo.mes
            )
        return queryset.none() 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mes_activo = MesActivo.objects.filter(activo=True).first()
        context['mes_activo'] = mes_activo
        return context


class RegistroConsumoCreateView(LoginRequiredMixin, CreateView):
    model = RegistroConsumo
    form_class = RegistroConsumoForm
    template_name = 'core/consumo_form.html'
    success_url = reverse_lazy('consumo-list')

    def get_initial(self):
        initial = super().get_initial()
        mes_activo = MesActivo.objects.filter(activo=True).first()
        if mes_activo:
            fecha_mes = datetime(mes_activo.año, mes_activo.mes, 1)
            precio = PrecioEnergia.objects.filter(fecha_registro=fecha_mes).first()
            if precio:
                initial['precio_kwh_mes'] = precio.valor_kwh
            return initial

    def form_valid(self, form):
        mes_activo = MesActivo.objects.filter(activo=True).first()
        if mes_activo:
            fecha_mes = datetime(mes_activo.año, mes_activo.mes, 1)
            try:
                precio = PrecioEnergia.objects.get(fecha_registro=fecha_mes)
                form.instance.precio_kwh = precio.valor_kwh
            except PrecioEnergia.DoesNotExist:
                form.instance.precio_kwh = 0  
        return super().form_valid(form)


class RegistroConsumoDeleteView(LoginRequiredMixin, DeleteView):
    model = RegistroConsumo
    template_name = 'core/consumo_confirm_delete.html'
    success_url = reverse_lazy('consumo-list')





def dashboard_view(request):
    registros = RegistroConsumo.objects.all()
    form = FiltroDashboardForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data['fecha_inicio']:
            registros = registros.filter(fecha__gte=form.cleaned_data['fecha_inicio'])
        if form.cleaned_data['fecha_fin']:
            registros = registros.filter(fecha__lte=form.cleaned_data['fecha_fin'])
        if form.cleaned_data['molde']:
            registros = registros.filter(molde=form.cleaned_data['molde'])

    # RESUMEN GENERAL
    total_horas = registros.aggregate(Sum('horas_trabajadas'))['horas_trabajadas__sum'] or 0
    total_piezas = registros.aggregate(Sum('piezas_producidas'))['piezas_producidas__sum'] or 0
    total_consumo = sum(r.consumo_estimado() for r in registros)
    total_costo = sum(r.costo_estimado_maquina() for r in registros)

    # CONSUMO POR MÁQUINA
    data_por_maquina = {}
    for r in registros:
        nombre = r.maquina.nombre
        data_por_maquina[nombre] = data_por_maquina.get(nombre, 0) + r.consumo_estimado()

    fig_consumo = go.Figure(data=[
        go.Bar(x=list(data_por_maquina.keys()), y=list(data_por_maquina.values()), marker_color='steelblue')
    ])
    fig_consumo.update_layout(title='🔋 Consumo energético por máquina (kWh)', xaxis_title='Máquina', yaxis_title='kWh')
    grafico_consumo = fig_consumo.to_html(full_html=False)

    # COSTO POR MÁQUINA
    data_costo_por_maquina = {}
    for r in registros:
        nombre = r.maquina.nombre
        data_costo_por_maquina[nombre] = data_costo_por_maquina.get(nombre, 0) + r.costo_estimado_maquina()

    fig_costo = go.Figure(data=[
        go.Bar(x=list(data_costo_por_maquina.keys()), y=list(data_costo_por_maquina.values()), marker_color='indianred')
    ])
    fig_costo.update_layout(title='💰 Costo energético total por máquina (COP)', xaxis_title='Máquina', yaxis_title='COP')
    grafico_costo = fig_costo.to_html(full_html=False)

    return render(request, 'core/dashboard.html', {
        'form': form,
        'grafico_consumo': grafico_consumo,
        'grafico_costo': grafico_costo,
        'total_horas': total_horas,
        'total_piezas': total_piezas,
        'total_consumo': total_consumo,
        'total_costo': total_costo
    })




class AsignacionListView(LoginRequiredMixin, ListView):
    model = MoldeMaquinariaAsignacion
    template_name = 'core/asignacion_list.html'
    context_object_name = 'asignaciones'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asignaciones = self.get_queryset()

        agrupadas = defaultdict(list)
        for a in asignaciones:
            agrupadas[a.molde].append(a)

        context['asignaciones_agrupadas'] = agrupadas
        return context

class AsignacionCreateView(LoginRequiredMixin, CreateView):
    model = MoldeMaquinariaAsignacion
    form_class = AsignacionForm
    template_name = 'core/asignacion_form.html'
    success_url = reverse_lazy('asignacion-list')


class AsignacionUpdateView(LoginRequiredMixin, UpdateView):
    model = MoldeMaquinariaAsignacion
    form_class = AsignacionForm
    template_name = 'core/asignacion_form.html'
    success_url = reverse_lazy('asignacion-list')


class AsignacionDeleteView(LoginRequiredMixin, DeleteView):
    model = MoldeMaquinariaAsignacion
    template_name = 'core/asignacion_confirm_delete.html'
    success_url = reverse_lazy('asignacion-list')



# Para el precio de la energia

class PrecioEnergiaView(UserPassesTestMixin, UpdateView):
    model = PrecioEnergia
    form_class = PrecioEnergiaForm
    template_name = 'core/precio_form.html'
    success_url = reverse_lazy('precio-historial')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


    
    def get_object(self):
        mes_activo = MesActivo.objects.filter(activo=True).first()
        if mes_activo:
            fecha_mes = datetime(mes_activo.año, mes_activo.mes, 1)
            precio, _ = PrecioEnergia.objects.get_or_create(
                fecha_registro=fecha_mes,
                defaults={'valor_kwh': 0}  # Se puede editar luego en el formulario
            )
            return precio
        return None

    def form_valid(self, form):
        # 🚨 Aquí es donde forzamos que la fecha tenga día 1
        mes_activo = MesActivo.objects.filter(activo=True).first()
        if mes_activo:
            form.instance.fecha_registro = datetime(mes_activo.año, mes_activo.mes, 1)
        return super().form_valid(form)
    

class PrecioEnergiaListView(LoginRequiredMixin, ListView):
    model = PrecioEnergia
    template_name = 'core/precio_list.html'
    context_object_name = 'precios'

    def get_queryset(self):
        return PrecioEnergia.objects.order_by('-fecha_registro') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mes_activo = MesActivo.objects.filter(activo=True).first()
        context["mes_activo"] = mes_activo
        return context
    


# ROI
class SimuladorROIView(FormView):
    template_name = 'core/roi_simulador.html'
    form_class = SimuladorROIForm

    def form_valid(self, form):
        maquina = form.cleaned_data['maquina']
        try:
            mes_activo = MesActivo.objects.filter(activo=True).first()
            precio_kwh = None
            if mes_activo:
                fecha_mes = datetime(mes_activo.año, mes_activo.mes, 1)
                precio = PrecioEnergia.objects.filter(fecha_registro=fecha_mes).first()
                if precio:
                    precio_kwh = precio.valor_kwh
        except PrecioEnergia.DoesNotExist:
            precio_kwh = None

        if precio_kwh is None:
            form.add_error(None, "No hay un precio del kWh registrado. Por favor, pídele al administrador que lo configure.")
            return self.form_invalid(form)
        
        porcentaje_ahorro = float(form.cleaned_data['porcentaje_ahorro'])
        costo_inversion = form.cleaned_data['costo_inversion']

        potencia_kw = maquina.potencia_watts / 1000

        # Obtener registros de esa máquina
        registros = RegistroConsumo.objects.filter(maquina=maquina)

        # Agrupar horas por mes
        horas_por_mes = defaultdict(float)
        for r in registros:
            clave = (r.fecha.year, r.fecha.month)
            horas_por_mes[clave] += r.horas_trabajadas

        if horas_por_mes:
            promedio_horas_mensuales = sum(horas_por_mes.values()) / len(horas_por_mes)
        else:
            promedio_horas_mensuales = 0

        consumo_mensual = potencia_kw * promedio_horas_mensuales
        costo_mensual_actual = consumo_mensual * precio_kwh
        ahorro_mensual = costo_mensual_actual * porcentaje_ahorro

        if ahorro_mensual > 0:
            tiempo_retorno_años = costo_inversion / (ahorro_mensual * 12)
        else:
            tiempo_retorno_años = None

        if tiempo_retorno_años is None:
            clasificacion = "No viable"
        elif tiempo_retorno_años < 1:
            clasificacion = "ROI Excelente (< 1 año)"
        elif tiempo_retorno_años < 2:
            clasificacion = "ROI Muy bueno (< 2 años)"
        elif tiempo_retorno_años <= 3:
            clasificacion = "ROI Aceptable (< 3 años)"
        else:
            clasificacion = "No viable (> 3 años)"

        contexto = {
            'form': form,
            'resultados': {
                'potencia_kw': potencia_kw,
                'horas_promedio': promedio_horas_mensuales,
                'consumo_mensual': consumo_mensual,
                'costo_mensual_actual': costo_mensual_actual,
                'ahorro_mensual': ahorro_mensual,
                'tiempo_retorno_años': tiempo_retorno_años,
                'clasificacion': clasificacion,
                'precio_kwh': precio_kwh
            }
        }
        return render(self.request, self.template_name, contexto)
    
class CambiarMesActivoView(UpdateView):
    model = MesActivo
    form_class = MesActivoForm
    template_name = 'core/mes_activo_form.html'

    def form_valid(self, form):
        MesActivo.objects.all().update(activo=False)
        form.instance.activo = True
        return super().form_valid(form)

    def get_success_url(self):
        return '/' 
    


class MesActivoUpdateView(LoginRequiredMixin, UpdateView):
    model = MesActivo
    form_class = MesActivoForm
    template_name = 'core/mes_activo_form.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return MesActivo.objects.first()
    


def obtener_maquinas_por_molde(request):
    molde_id = request.GET.get('molde_id')
    maquinas = []

    if molde_id:
        asignaciones = MoldeMaquinariaAsignacion.objects.filter(molde_id=molde_id)
        maquinas = [{"id": a.maquina.id, "nombre": f"{a.maquina.nombre} (ID: {a.maquina.id})"} for a in asignaciones]

    return JsonResponse(maquinas, safe=False)