from django.views.generic import TemplateView
from core.models import RegistroConsumo, MesActivo, PrecioEnergia
from collections import defaultdict
from datetime import datetime
from .forms import InversionForm

class ROIRealView(TemplateView):
    template_name = 'roi/roi_real.html'

    def post(self, request, *args, **kwargs):
        form = InversionForm(request.POST)
        if form.is_valid():
            self.request.session['inversion'] = form.cleaned_data['inversion']
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mes_activo = MesActivo.objects.filter(activo=True).first()

        if not mes_activo:
            context['error'] = "No hay un mes activo definido."
            return context

        # Obtener inversión
        inversion = self.request.session.get('inversion', 100000)
        form = InversionForm(initial={'inversion': inversion})

        context['form'] = form
        context['inversion'] = inversion

        registros = RegistroConsumo.objects.filter(
            fecha__year=mes_activo.año,
            fecha__month=mes_activo.mes
        )

        precio_obj = PrecioEnergia.objects.filter(
            fecha_registro=datetime(mes_activo.año, mes_activo.mes, 1)
        ).first()

        if not precio_obj:
            context['error'] = "No hay precio energético registrado para el mes activo."
            return context

        precio_kwh_mes = precio_obj.valor_kwh

        datos_por_maquina = defaultdict(lambda: {
            'horas': 0,
            'consumo': 0,
        })

        for r in registros:
            nombre_maquina = r.maquina.nombre
            datos = datos_por_maquina[nombre_maquina]
            datos['horas'] += r.horas_trabajadas
            datos['consumo'] += r.consumo_estimado()

        def clasificar(roi):
            if roi is None:
                return "No calculado", ""
            if roi < 1:
                return "Excelente", "Recuperación inmediata. Alta prioridad de optimización."
            elif roi < 2:
                return "Muy bueno", "Recuperación rápida. Implementación prioritaria."
            elif roi < 3:
                return "Bueno", "Viable si hay recursos. Recomendado."
            elif roi < 5:
                return "Aceptable", "Retorno moderado. No urgente."
            elif roi < 7:
                return "Poco atractivo", "Largo retorno. Evaluar otras opciones."
            else:
                return "No viable", "Retorno demasiado lento. No recomendable."

        datos_lista = []

        for nombre, d in datos_por_maquina.items():
            # Ecuación 1: Ahorro energético (kWh)
            ahorro_20_kwh = d['consumo'] * 0.20
            ahorro_30_kwh = d['consumo'] * 0.30

            # Ecuación 2: Ahorro en COP
            ahorro_20_cop = ahorro_20_kwh * precio_kwh_mes
            ahorro_30_cop = ahorro_30_kwh * precio_kwh_mes

            # ROI basado en ahorro anual
            ahorro_anual_20 = ahorro_20_cop * 12
            ahorro_anual_30 = ahorro_30_cop * 12

            roi_20 = round(inversion / ahorro_anual_20, 2) if ahorro_anual_20 > 0 else None
            roi_30 = round(inversion / ahorro_anual_30, 2) if ahorro_anual_30 > 0 else None

            clas_20, concl_20 = clasificar(roi_20)
            clas_30, concl_30 = clasificar(roi_30)

            datos_lista.append({
                'maquina': nombre,
                'horas': d['horas'],
                'consumo': d['consumo'],
                'ahorro_20_kwh': ahorro_20_kwh,
                'ahorro_30_kwh': ahorro_30_kwh,
                'ahorro_20_cop': ahorro_20_cop,
                'ahorro_30_cop': ahorro_30_cop,
                'roi_20': roi_20,
                'roi_30': roi_30,
                'clasificacion_20': clas_20,
                'clasificacion_30': clas_30,
                'conclusion_20': concl_20,
                'conclusion_30': concl_30,
            })

        context.update({
            'datos': datos_lista,
            'mes_activo': mes_activo,
            'precio_kwh': precio_kwh_mes,
        })
        return context

