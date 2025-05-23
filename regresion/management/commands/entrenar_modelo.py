from django.core.management.base import BaseCommand
from regresion.ml.train_model import entrenar_modelo

class Command(BaseCommand):
    help = 'Entrena el modelo de predicción energética con los datos reales'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando entrenamiento del modelo...")
        entrenar_modelo()
        self.stdout.write(self.style.SUCCESS("Entrenamiento finalizado correctamente."))


