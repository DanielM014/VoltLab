from .models import MesActivo

def obtener_mes_activo():
    return MesActivo.objects.filter(activo=True).first()
