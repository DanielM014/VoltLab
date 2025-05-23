from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from datetime import date
from django.utils import timezone


USER_ROLES = (
    ('operario', 'Operario'),
    ('supervisor', 'Supervisor'),
    ('admin', 'Administrador'),
)


class MoldeMaquinariaAsignacion(models.Model):
    molde = models.ForeignKey('Molde', on_delete=models.CASCADE, related_name='asignaciones')
    maquina = models.ForeignKey('Maquinaria', on_delete=models.CASCADE)
    piezas_asignadas = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.molde.nombre} - {self.maquina.nombre}: {self.piezas_asignadas} piezas"

class CustomUser(AbstractUser):
    rol = models.CharField(max_length=20, choices=USER_ROLES, default='operario')

    def __str__(self):
        return f"{self.username} ({self.rol})"

class Maquinaria(models.Model):
    nombre = models.CharField(max_length=100)
    potencia_watts = models.PositiveIntegerField(null=True, blank=True)
    voltaje = models.FloatField(null=True, blank=True)   
    corriente = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    def potencia_kw(self):
        return round(self.potencia_watts / 1000, 2)

    
class Molde(models.Model):
    nombre = models.CharField(max_length=100)
    piezas_necesarias = models.PositiveIntegerField()
    maquinas_compatibles = models.ManyToManyField(
        Maquinaria,
        through='MoldeMaquinariaAsignacion',
        related_name='moldes_compatibles'
    )

    def __str__(self):
        return self.nombre


class RegistroConsumo(models.Model):
    operario = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    maquina = models.ForeignKey(Maquinaria, on_delete=models.CASCADE)
    molde = models.ForeignKey(Molde, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today)
    horas_trabajadas = models.FloatField()
    piezas_producidas = models.PositiveIntegerField()

    fecha_registro = models.DateField(auto_now_add=True)
    fecha_hipotetica_finalizacion = models.DateField(null=True, blank=True)
    precio_kwh_mes = models.FloatField(
    help_text="Precio del kWh según el promedio mensual (en COP)",
    null=True, blank=True
    )

    def calcular_fecha_finalizacion(self):
        horas_restantes = self.horas_trabajadas
        fecha_actual = self.fecha

        while horas_restantes > 0:
            dia_semana = fecha_actual.weekday()  # 0=lunes, 6=domingo

            if dia_semana in range(0, 5):  # Lunes a viernes
                jornada = 10
            elif dia_semana == 5:  # Sábado
                jornada = 6
            else:
                jornada = 0  # Domingo

            if jornada > 0:
                horas_restantes -= jornada

            fecha_actual += timedelta(days=1)

        return fecha_actual

    def save(self, *args, **kwargs):
        if self.fecha and self.horas_trabajadas:
            self.fecha_hipotetica_finalizacion = self.calcular_fecha_finalizacion()
        super().save(*args, **kwargs)
    
    
    def consumo_estimado(self):
    # Convertir watts a kW
        potencia_kw = self.maquina.potencia_watts / 1000
        return round(potencia_kw * self.horas_trabajadas, 2)


    def costo_estimado(self):
        return round(self.consumo_estimado() * self.precio_kwh_mes, 2)

    def costo_estimado_maquina(self):
        potencia_kw = self.maquina.potencia_watts / 1000
        return round((potencia_kw * self.horas_trabajadas) * self.precio_kwh_mes, 2)



    def __str__(self):
        return f"{self.maquina} - {self.fecha}"
    

class PrecioEnergia(models.Model):
    valor_kwh = models.FloatField(help_text="Precio del kWh según el recibo (COP)")
    fecha_registro = models.DateField(unique=True)

    def __str__(self):
        return f"{self.valor_kwh} COP (registrado el {self.fecha_registro})"

    class Meta:
        ordering = ['-fecha_registro']


class MesActivo(models.Model):
    mes = models.IntegerField(choices=[(i, timezone.datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)])
    año = models.IntegerField()
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('mes', 'año')

    def __str__(self):
        return f"{timezone.datetime(self.año, self.mes, 1).strftime('%B')} {self.año}"
