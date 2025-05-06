from django.shortcuts import render
from django.views.generic import FormView
from django.urls import reverse_lazy
from regresion.forms import PrediccionConsumoForm
from regresion.ml.utils import cargar_modelo_y_predecir
from django.views.generic import TemplateView
from core.models import RegistroConsumo, MesActivo
from regresion.ml.predictor import predecir_consumo
import plotly.graph_objs as go
import plotly.offline as opy
from django.utils.html import format_html

class ComparacionModeloView(TemplateView):
    template_name = "regresion/comparacion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mes = MesActivo.objects.filter(activo=True).first()

        if not mes:
            context["error"] = "No hay mes activo definido."
            return context

        registros = RegistroConsumo.objects.select_related('maquina').filter(
            fecha__year=mes.año, fecha__month=mes.mes
        )

        comparaciones = []
        for r in registros:
            predicho = predecir_consumo(
                potencia_kw=r.maquina.potencia_kw() if callable(r.maquina.potencia_kw) else r.maquina.potencia_kw,
                horas_trabajadas=r.horas_trabajadas,
                piezas_producidas=r.piezas_producidas,
                precio_kwh=r.precio_kwh_mes
            )

            real = r.consumo_estimado()
            diferencia = predicho - real if predicho is not None else None

            comparaciones.append({
                "registro": r,
                "real": real,
                "predicho": predicho,
                "diferencia": diferencia,
            })

        labels = [f"{r.molde.nombre}-{r.maquina.nombre}" for r in registros]
        real = [c["real"] for c in comparaciones]
        predicho = [c["predicho"] for c in comparaciones]

        trace1 = go.Bar(x=labels, y=real, name='Real')
        trace2 = go.Bar(x=labels, y=predicho, name='Predicho')

        layout = go.Layout(barmode='group', title='Consumo Real vs Predicho')
        fig = go.Figure(data=[trace1, trace2], layout=layout)
        div = opy.plot(fig, auto_open=False, output_type='div')

        context["plot_div"] = div
        context["comparaciones"] = comparaciones
        context["mes_activo"] = mes
        return context

# 🚀 Nuevo sistema mejorado de conclusiones
def evaluar_prediccion(predicho, potencia_kw, horas_trabajadas):
    if potencia_kw is None or horas_trabajadas is None:
        return format_html("<span style='color:gray;'>Datos incompletos para evaluación.</span>")

    esperado = potencia_kw * horas_trabajadas
    if esperado == 0:
        return format_html("<span style='color:gray;'>Valor esperado es 0. No se puede evaluar.</span>")

    desviacion = ((predicho - esperado) / esperado) * 100

    if desviacion <= -30:
        conclusion = "⚠️ <span style='color:red;'>Consumo predicho muy bajo. Riesgo de subestimación severa.</span>"
    elif desviacion <= -10:
        conclusion = "⚠️ <span style='color:orange;'>Consumo predicho algo bajo. Verifica parámetros de entrada.</span>"
    elif desviacion <= 10:
        conclusion = "✅ <span style='color:green;'>Consumo predicho razonable y coherente.</span>"
    elif desviacion <= 30:
        conclusion = "⚠️ <span style='color:orange;'>Consumo predicho algo alto. Podría indicar sobreestimación leve.</span>"
    else:
        conclusion = "⚠️ <span style='color:red;'>Consumo predicho muy alto. Verifica eficiencia de la máquina o datos ingresados.</span>"

    return format_html(conclusion)

class PrediccionConsumoView(FormView):
    template_name = 'regresion/prediccion_consumo.html'
    form_class = PrediccionConsumoForm
    success_url = reverse_lazy('prediccion-consumo')

    def form_valid(self, form):
        molde = form.cleaned_data['molde']
        maquina = form.cleaned_data['maquina']
        horas = form.cleaned_data['horas_trabajadas']
        piezas = form.cleaned_data['piezas_producidas']
        precio_kwh = form.cleaned_data['precio_kwh']

        potencia = maquina.potencia_kw() if callable(maquina.potencia_kw) else maquina.potencia_kw
        prediccion = cargar_modelo_y_predecir(
            potencia,
            horas,
            piezas,
            precio_kwh
        )

        costo_estimado = prediccion * precio_kwh  # 🚀 NUEVO: costo en COP
        conclusion = evaluar_prediccion(prediccion, potencia, horas)

        return self.render_to_response(self.get_context_data(
            form=form,
            prediccion=prediccion,
            costo_estimado=costo_estimado,
            conclusion=conclusion,
            enviada=True
        ))