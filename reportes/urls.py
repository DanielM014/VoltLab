from django.urls import path
from .views import exportar_reporte_excel

urlpatterns = [
    path("excel/", exportar_reporte_excel, name="exportar-reporte-excel"),
]
