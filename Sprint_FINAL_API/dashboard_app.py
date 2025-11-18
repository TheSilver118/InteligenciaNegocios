import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Configuración Inicial ---
# Reemplaza con la URL correcta si tu API no se ejecuta en este puerto/dirección
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Dashboard de Recomendación de Criptomonedas",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Dashboard de Recomendación de Criptomonedas")
st.caption("Interfaz visual que consume la API de clustering y recomendaciones de FastAPI.")

# ----------------------------------------------------------------------------------
# 1. Función para la Predicción
# ----------------------------------------------------------------------------------
def get_prediction(data):
    """Llama al endpoint /predict para obtener el clúster."""
    try:
        response = requests.post(f"{API_URL}/predict", json=data)
        response.raise_for_status() # Lanza error para códigos 4xx/5xx
        return response.json().get("cluster")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al conectar o procesar la API de Predicción: {e}")
        return None

# ----------------------------------------------------------------------------------
# 2. Función para las Recomendaciones
# ----------------------------------------------------------------------------------
def get_recommendations(cluster):
    """Llama al endpoint /recommendations para obtener las criptomonedas."""
    try:
        response = requests.get(f"{API_URL}/recommendations?cluster={cluster}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al conectar o procesar la API de Recomendaciones: {e}")
        return None

# ----------------------------------------------------------------------------------
# 3. Sidebar y Formulario de Predicción
# ----------------------------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Predicción del Perfil de Inversión")
    st.markdown("Ingresa las métricas para clasificar el perfil y obtener recomendaciones.")
    
    with st.form("perfil_form"):
        # Campos de entrada con valores por defecto (ejemplo de BTC/ETH)
        open_val = st.number_input("Open", value=50000.0, format="%.2f", key="open")
        high_val = st.number_input("High", value=51000.0, format="%.2f", key="high")
        low_val = st.number_input("Low", value=49000.0, format="%.2f", key="low")
        close_val = st.number_input("Close", value=50500.0, format="%.2f", key="close")
        volumeto_val = st.number_input("VolumeTo", value=1000000.0, format="%.2f", key="volumeto")
        
        submitted = st.form_submit_button("Analizar Perfil e Iniciar Búsqueda")

# ----------------------------------------------------------------------------------
# 4. Lógica Principal y Visualización de Resultados
# ----------------------------------------------------------------------------------
if submitted:
    # 1. Obtener el clúster
    feature_data = {
        "open": open_val,
        "high": high_val,
        "low": low_val,
        "close": close_val,
        "volumeto": volumeto_val
    }
    
    cluster_predicho = get_prediction(feature_data)
    
    if cluster_predicho is not None:
        st.success(f"✅ *Perfil Clasificado:* El perfil pertenece al Clúster *{cluster_predicho}*")
        
        # 2. Obtener las recomendaciones
        rec_data = get_recommendations(cluster_predicho)
        
        if rec_data:
            st.header("📊 Recomendaciones y Estadísticas")
            
            # Convertir el detalle de recomendaciones a DataFrame para visualización
            # El detalle contiene {coin: avg_close}
            rec_detail = rec_data.get("detalle", {})
            df_recs = pd.DataFrame(
                list(rec_detail.items()), 
                columns=["Criptomoneda", "Cierre Promedio ($)"]
            )
            df_recs["Clúster"] = f"Clúster {cluster_predicho}"

            col1, col2 = st.columns([2, 3])

            with col1:
                st.subheader(f"🥇 Top 3 Recomendaciones (Clúster {cluster_predicho})")
                st.dataframe(
                    df_recs.style.format({"Cierre Promedio ($)": "${:,.2f}"}), 
                    hide_index=True,
                    use_container_width=True
                )
                st.markdown(
                    f"*Mensaje:* Estas son las criptomonedas con el mayor precio de *Cierre Promedio* en el Clúster *{cluster_predicho}*, sugiriendo potencial de inversión basado en su comportamiento histórico."
                )

            with col2:
                st.subheader("Gráfico de Cierre Promedio")
                # Gráfico dinámico con Plotly (a través de Streamlit)
                fig = px.bar(
                    df_recs, 
                    x="Criptomoneda", 
                    y="Cierre Promedio ($)",
                    color="Criptomoneda",
                    title=f"Valor Promedio de Cierre por Criptomoneda en el Clúster {cluster_predicho}",
                    template="seaborn"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Introduce un perfil de inversión en el panel lateral para obtener las recomendaciones y estadísticas.")

st.markdown("---")

# ----------------------------------------------------------------------------------
# 5. (Opcional) Sección de Historial
# ----------------------------------------------------------------------------------
st.header("🕰 Historial de Búsquedas")
# Llama al endpoint de historial para mostrar el estado
try:
    history_response = requests.get(f"{API_URL}/history")
    history_response.raise_for_status()
    st.code(history_response.json().get("historial"), language="json")
    st.warning("Esta funcionalidad sigue pendiente de conexión a una base de datos, según la API.")
except requests.exceptions.RequestException:
    st.error("No se pudo conectar con el endpoint /history de la API.")