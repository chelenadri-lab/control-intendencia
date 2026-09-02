import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Control Oposición Intendencia", layout="wide")

DB_FILE = "seguimiento_opositores.csv"

ALUMNOS_LISTA = [
    "Estrella Alcoba", "Carmen Andrés Albaladejo", "Carlos Báez Gutiérrez", 
    "Alberto Bravo", "Javier Carreras", "Cristian Carrillo", "Fernando Casanova", 
    "Nieves de Loresecha Palma", "Cristian Dorado", "Enrique Flores Carretero", 
    "Nicolás Ibáñez", "Fermín Maeztu", "Gonzalo Martínez", "Christian Morales", 
    "Pablo Noya Marín", "Diego Olías", "Paula Panadero", "Marcos Rivero López", 
    "José María Rodríguez", "María Serrano Galindo", "Gonzalo Suero", 
    "Adrián Valenzuela", "Erik Arnold Van Lieshout", "Daniel Varas del Peso"
]

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        df_inicial = pd.DataFrame(columns=[
            "Fecha", "Alumno", "Bloque", "Tema_Escrito", 
            "Tiempo_Minutos", "Feedback_Cualitativo"
        ])
        df_inicial.to_csv(DB_FILE, index=False)
        return df_inicial

df_seguimiento = cargar_datos()

st.title("🎯 Control de Temas Vivos e Insaculación - Intendencia")
st.markdown("Gestión ágil para seguimiento cualitativo de opositores (Sin notas numéricas)")

menu = st.sidebar.selectbox("Menú de Navegación", ["Registrar Nueva Lectura / Insaculación", "Consultar Histórico por Alumno"])

bloques_oposition = [
    "Hacienda Pública (14)", 
    "Constitucional / Administrativo (41)", 
    "Derecho Financiero y Sistema Fiscal (20)", 
    "Economía (12)", 
    "Contabilidad (15)"
]

if menu == "Registrar Nueva Lectura / Insaculación":
    st.subheader("📝 Registrar Sesión de Insaculación / Redacción")
    
    with st.form("form_lectura"):
        col1, col2 = st.columns(2)
        with col1:
            alumno_sel = st.selectbox("Opositor", ALUMNOS_LISTA)
            bloque_sel = st.selectbox("Bloque de Materia", bloques_oposition)
        with col2:
            fecha_sel = st.date_input("Fecha de Lectura", datetime.today())
            tema_escrito = st.text_input("Tema o Epígrafe Concreto (Ej: Tema 8 - El Presupuesto)")
            
        tiempo_redaccion = st.slider("Tiempo empleado (minutos)", 30, 90, 60)
        
        feedback = st.text_area(
            "Diagnóstico Cualitativo (Estructura, tiempo, lagunas normativas, claridad...)", 
            placeholder="Ej: Buena estructura inicial, pero se extendió demasiado en la introducción..."
        )
        
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            nuevo_registro = pd.DataFrame({
                "Fecha": [str(fecha_sel)],
                "Alumno": [alumno_sel],
                "Bloque": [bloque_sel],
                "Tema_Escrito": [tema_escrito],
                "Tiempo_Minutos": [tiempo_redaccion],
                "Feedback_Cualitativo": [feedback]
            })
            
            df_seguimiento = pd.concat([df_seguimiento, nuevo_registro], ignore_index=True)
            df_seguimiento.to_csv(DB_FILE, index=False)
            st.success(f"¡Registro guardado correctamente para {alumno_sel}!")

elif menu == "Consultar Histórico por Alumno":
    st.subheader("📊 Histórico y Evolución del Opositor")
    
    alumno_filtro = st.selectbox("Selecciona al opositor para ver su expediente", ALUMNOS_LISTA)
    
    df_alumno = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
    
    if not df_alumno.empty:
        st.metric(label="Total de temas/ensayos registrados", value=len(df_alumno))
        st.dataframe(df_alumno[["Fecha", "Bloque", "Tema_Escrito", "Tiempo_Minutos", "Feedback_Cualitativo"]], use_container_width=True)
    else:
        st.info("Aún no hay registros de lecturas para este opositor.")
