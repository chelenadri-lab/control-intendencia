import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Control Oposición Intendencia", layout="wide")

DB_ALUMNOS = "alumnos_intendencia.csv"
DB_SEGUIMIENTO = "seguimiento_opositores.csv"

# Lista inicial por defecto si no existe archivo de alumnos
ALUMNOS_INICIALES = [
    "Estrella Alcoba", "Carmen Andrés Albaladejo", "Carlos Báez Gutiérrez", 
    "Alberto Bravo", "Javier Carreras", "Cristian Carrillo", "Fernando Casanova", 
    "Nieves de Loresecha Palma", "Cristian Dorado", "Enrique Flores Carretero", 
    "Nicolás Ibáñez", "Fermín Maeztu", "Gonzalo Martínez", "Christian Morales", 
    "Pablo Noya Marín", "Diego Olías", "Paula Panadero", "Marcos Rivero López", 
    "José María Rodríguez", "María Serrano Galindo", "Gonzalo Suero", 
    "Adrián Valenzuela", "Erik Arnold Van Lieshout", "Daniel Varas del Peso"
]

bloques_oposition = [
    "Hacienda Pública (14)", 
    "Constitucional / Administrativo (41)", 
    "Derecho Financiero y Sistema Fiscal (20)", 
    "Economía (12)", 
    "Contabilidad (15)"
]

# Funciones de carga de datos
def cargar_alumnos():
    if os.path.exists(DB_ALUMNOS):
        df = pd.read_csv(DB_ALUMNOS)
        return df["Alumno"].tolist()
    else:
        df = pd.DataFrame({"Alumno": ALUMNOS_INICIALES})
        df.to_csv(DB_ALUMNOS, index=False)
        return ALUMNOS_INICIALES

def guardar_lista_alumnos(lista):
    df = pd.DataFrame({"Alumno": lista})
    df.to_csv(DB_ALUMNOS, index=False)

def cargar_seguimiento():
    if os.path.exists(DB_SEGUIMIENTO):
        return pd.read_csv(DB_SEGUIMIENTO)
    else:
        df_inicial = pd.DataFrame(columns=[
            "Fecha", "Alumno", "Bloque", "Temas_Para_Esta_Semana", 
            "Tema_Escrito", "Tiempo_Minutos", "Feedback_Cualitativo"
        ])
        df_inicial.to_csv(DB_SEGUIMIENTO, index=False)
        return df_inicial

lista_alumnos = cargar_alumnos()
df_seguimiento = cargar_seguimiento()

# Menú lateral
st.sidebar.title("📌 Menú de Control")
menu = st.sidebar.selectbox("Selecciona una opción", [
    "📝 Registrar Sesión / Ficha Semanal", 
    "📊 Cuadro Resumen y Progreso", 
    "👥 Gestión de Opositores (Añadir / Borrar)",
    "📊 Histórico por Alumno"
])

if menu == "📝 Registrar Sesión / Ficha Semanal":
    st.subheader("📝 Ficha de Seguimiento y Control Semanal")
    
    if not lista_alumnos:
        st.warning("No hay alumnos registrados. Añade opositores en la pestaña del menú lateral.")
    else:
        with st.form("form_lectura"):
            col1, col2 = st.columns(2)
            with col1:
                alumno_sel = st.selectbox("Opositor", lista_alumnos)
                bloque_sel = st.selectbox("Bloque de Materia", bloques_oposition)
            with col2:
                fecha_sel = st.date_input("Fecha de Sesión", datetime.today())
                temas_semana = st.text_input("Temas que lleva para esta semana (Ej: Temas 5 al 9)")
                
            tema_escrito = st.text_input("Tema escrito / Insaculado en clase (Opcional)")
            tiempo_redaccion = st.slider("Tiempo empleado en exposición/redacción (minutos)", 30, 90, 60)
            
            feedback = st.text_area(
                "Diagnóstico Cualitativo (Estructura, tiempo, lagunas normativas, claridad...)", 
                placeholder="Ej: Buena estructura inicial, pero se extendió demasiado en el epígrafe 2..."
            )
            
            submitted = st.form_submit_button("Guardar Registro")
            
            if submitted:
                nuevo_registro = pd.DataFrame({
                    "Fecha": [str(fecha_sel)],
                    "Alumno": [alumno_sel],
                    "Bloque": [bloque_sel],
                    "Temas_Para_Esta_Semana": [temas_semana],
                    "Tema_Escrito": [tema_escrito],
                    "Tiempo_Minutos": [tiempo_redaccion],
                    "Feedback_Cualitativo": [feedback]
                })
                
                df_seguimiento = pd.concat([df_seguimiento, nuevo_registro], ignore_index=True)
                df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success(f"¡Ficha guardada correctamente para {alumno_sel}!")

elif menu == "📊 Cuadro Resumen y Progreso":
    st.subheader("📊 Cuadro Resumen General de Progreso")
    
    if df_seguimiento.empty:
        st.info("Todavía no hay registros guardados para mostrar el resumen.")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total de Sesiones / Ensayos Registrados", len(df_seguimiento))
        with col_m2:
            st.metric("Opositores con Actividad", df_seguimiento["Alumno"].nunique())
        
        st.markdown("### 📈 Progreso Total por Alumno (Nº de revisiones/temas tocados)")
        resumen_alumnos = df_seguimiento.groupby("Alumno").size().reset_index(name="Temas / Revisiones Totales")
        resumen_alumnos = resumen_alumnos.sort_values(by="Temas / Revisiones Totales", ascending=False)
        st.dataframe(resumen_alumnos, use_container_width=True)
        
        st.markdown("### 🧱 Cobertura por Bloques de Materia")
        resumen_bloques = df_seguimiento.groupby("Bloque").size().reset_index(name="Veces Practicado")
        st.dataframe(resumen_bloques, use_container_width=True)

elif menu == "👥 Gestión de Opositores (Añadir / Borrar)":
    st.subheader("👥 Administrar Lista de Alumnos")
    
    st.markdown("### ➕ Añadir Nuevo Opositor")
    nuevo_nombre = st.text_input("Nombre y Apellidos del Opositor")
    if st.button("Añadir Opositor"):
        if nuevo_nombre and nuevo_nombre not in lista_alumnos:
            lista_alumnos.append(nuevo_nombre)
            guardar_lista_alumnos(lista_alumnos)
            st.success(f"¡{nuevo_nombre} añadido correctamente! Recarga la página si es necesario.")
        else:
            st.error("El nombre está vacío o ya existe en la lista.")
            
    st.markdown("---")
    st.markdown("### ❌ Eliminar o Modificar Opositor")
    alumno_a_borrar = st.selectbox("Selecciona opositor a eliminar", lista_alumnos)
    if st.button("Eliminar Opositor Seleccionado"):
        if alumno_a_borrar in lista_alumnos:
            lista_alumnos.remove(alumno_a_borrar)
            guardar_lista_alumnos(lista_alumnos)
            st.success(f"Se ha eliminado a {alumno_a_borrar} de la lista.")
            st.rerun()

elif menu == "📊 Histórico por Alumno":
    st.subheader("📊 Histórico y Evolución Individual")
    
    if not lista_alumnos:
        st.info("No hay alumnos.")
    else:
        alumno_filtro = st.selectbox("Selecciona al opositor", lista_alumnos)
        df_alumno = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
        
        if not df_alumno.empty:
            st.metric(label="Total de registros del alumno", value=len(df_alumno))
            st.dataframe(df_alumno[["Fecha", "Bloque", "Temas_Para_Esta_Semana", "Tema_Escrito", "Tiempo_Minutos", "Feedback_Cualitativo"]], use_container_width=True)
        else:
            st.info("Aún no hay registros guardados para este opositor.")
