import joblib
import numpy as np

def cargar_modelo_y_predecir(potencia_kw, horas, piezas, precio_kwh):
    modelo = joblib.load('modelo_consumo.pkl')
    entrada = np.array([[potencia_kw, horas, piezas, precio_kwh]])
    prediccion = modelo.predict(entrada)[0]
    return round(prediccion, 2)
