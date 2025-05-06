from django.shortcuts import render
import openpyxl
from openpyxl.styles import Font
from django.http import HttpResponse
from core.models import RegistroConsumo, MesActivo
from regresion.ml.predictor import predecir_consumo

def exportar_reporte_excel(request):
    mes = MesActivo.objects.filter(activo=True).first()
    if not mes:
        return HttpResponse("No hay mes activo", status=400)

    registros = RegistroConsumo.objects.select_related('maquina', 'molde').filter(
        fecha__month=mes.mes, fecha__year=mes.año
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Reporte {mes.mes}-{mes.año}"

    headers = [
        "Fecha", "Molde", "Máquina", "Horas", "Piezas", 
        "Consumo Real (kWh)", "Costo (COP)", 
        "Consumo Predicho (kWh)", "Diferencia"
    ]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    for r in registros:
        real = r.consumo_estimado()
        predicho = predecir_consumo(
            r.maquina.potencia_kw() if callable(r.maquina.potencia_kw) else r.maquina.potencia_kw,
            r.horas_trabajadas,
            r.piezas_producidas,
            r.precio_kwh_mes
        )
        diferencia = predicho - real if predicho is not None else None

        ws.append([
            r.fecha.strftime('%Y-%m-%d'),
            r.molde.nombre,
            r.maquina.nombre,
            r.horas_trabajadas,
            r.piezas_producidas,
            round(real, 2),
            round(r.costo_estimado(), 2),
            predicho,
            round(diferencia, 2) if diferencia is not None else "N/A"
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"Reporte_VoltLAB_{mes.mes}_{mes.año}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response
