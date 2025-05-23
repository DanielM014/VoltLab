import joblib
import numpy as np

def cargar_modelo():
    try:
        modelo = joblib.load("modelo_consumo.pkl")
        return modelo
    except Exception as e:
        print("Error cargando modelo:", e)
        return None

def predecir_consumo(potencia_kw, horas_trabajadas, piezas_producidas, precio_kwh):
    modelo = cargar_modelo()
    if modelo is None:
        return None

    entrada = np.array([[potencia_kw, horas_trabajadas, piezas_producidas, precio_kwh]])
    prediccion = modelo.predict(entrada)
    return round(prediccion[0], 2)
