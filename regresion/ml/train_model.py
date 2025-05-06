import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import joblib

from core.models import RegistroConsumo

def entrenar_modelo():
    registros = RegistroConsumo.objects.select_related('maquina').all()

    if not registros.exists():
        print("No hay registros suficientes para entrenar.")
        return

    data = []
    for r in registros:
        data.append({
            "potencia_kw": r.maquina.potencia_kw(),
            "horas_trabajadas": r.horas_trabajadas,
            "piezas_producidas": r.piezas_producidas,
            "precio_kwh": r.precio_kwh_mes,
            "consumo_real": r.consumo_estimado(),
        })

    df = pd.DataFrame(data)
    print("Dataset listo para entrenamiento:")
    print(df.head())

    X = df.drop("consumo_real", axis=1)
    y = df["consumo_real"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    print(f"Entrenamiento completo | R²: {r2:.4f} | MSE: {mse:.2f}")

    joblib.dump(modelo, 'modelo_consumo.pkl')
    print("Modelo guardado en 'modelo_consumo.pkl'")
