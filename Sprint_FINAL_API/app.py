from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

# ---------------------------------------------------
# 1. Inicializar la aplicación FastAPI
# ---------------------------------------------------
app = FastAPI(
    title="API de Recomendación de Criptomonedas",
    description="API que ofrece recomendaciones basadas en clustering de criptomonedas",
    version="1.0"
)

# ---------------------------------------------------
# 2. Cargar el modelo de clustering entrenado
# ---------------------------------------------------
try:
    model = joblib.load("model/modelo_clustering.pkl")
    df = pd.read_csv("data/criptomonedas_crypto_compare.csv")
except Exception as e:
    model = None
    df = None
    print(" Error cargando modelo o datos:", e)


# ---------------------------------------------------
# 3. Definir los esquemas de entrada
# ---------------------------------------------------
class InvestmentProfile(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volumeto: float


# ---------------------------------------------------
# 4. Endpoint de verificación (health check)
# ---------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": " API activa y funcionando correctamente"}


# ---------------------------------------------------
# 5. Endpoint de predicción (POST)
# ---------------------------------------------------
@app.post("/predict")
def predict(profile: InvestmentProfile):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")

    # Crear el DataFrame con las columnas esperadas por el modelo
    features = pd.DataFrame([{
        "open": profile.open,
        "high": profile.high,
        "low": profile.low,
        "close": profile.close,
        "volumeto": profile.volumeto
    }])

    # Realizar la predicción del clúster
    cluster = int(model.predict(features)[0])

    return {"cluster": cluster, "mensaje": f"El perfil pertenece al clúster {cluster}"}


# ---------------------------------------------------
# 6. Endpoint de recomendaciones
# ---------------------------------------------------
@app.get("/recommendations")
def get_recommendations(cluster: int):
    if df is None:
        raise HTTPException(status_code=500, detail="Datos no disponibles")

    # Selecciona criptos con mayor cierre promedio por clúster
    recomendaciones = (
        df.groupby("coin")["close"].mean().sort_values(ascending=False).head(3)
    )

    return {
        "cluster": cluster,
        "recomendaciones": recomendaciones.index.tolist(),
        "detalle": recomendaciones.to_dict()
    }


# ---------------------------------------------------
# 7. (Opcional) Endpoint de historial
# ---------------------------------------------------
@app.get("/history")
def get_history():
    return {"historial": "Funcionalidad pendiente de conexión con base de datos"}
