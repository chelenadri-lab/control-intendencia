import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Control Oposición Intendencia", layout="wide")

DB_ALUMNOS = "alumnos_intendencia_perfiles.csv"
DB_SEGUIMIENTO = "seguimiento_opositores.csv"

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
    "Hacienda Pública", 
    "Constitucional", 
    "Derecho Administrativo", 
    "Derecho Financiero y Sistema Fiscal", 
    "Economía", 
    "Contabilidad"
]

# Funciones de gestión de perfiles de alumnos
def cargar_alumnos():
    if os.path.exists(DB_ALUMNOS):
        return pd.read_csv(DB_ALUMNOS)
    else:
        df = pd.DataFrame({
            "Alumno": ALUMNOS_INICIALES,
            "Telefono": ["" for _ in ALUMNOS_INICIALES],
            "Correo": ["" for _ in ALUMNOS_INICIALES],
            "Circunstancias": ["" for _ in ALUMNOS_INICIALES]
        })
        df.to_csv(DB_ALUMNOS, index=False)
        return df

def guardar_alumnos(df):
    df.to_csv(DB_ALUMNOS, index=False)

def cargar_seguimiento():
    if os.path.exists(DB_SEGUIMIENTO):
        return pd.read_csv(DB_SEGUIMIENTO)
    else:
        df_inicial = pd.DataFrame(columns=[
            "Fecha", "Alumno", "Bloque", "Temas_Para_Esta_Semana", 
            "Tema_Escrito", "Tiempo_Minutos", "Estado_Semaforo", 
            "Errores_Frecuentes", "Feedback_Cualitativo"
        ])
        df_inicial.to_csv(DB_SEGUIMIENTO, index=False)
        return df_inicial

df_alumnos_db = cargar_alumnos()
lista_alumnos = df_alumnos_db["Alumno"].tolist()
df_seguimiento = cargar_seguimiento()

st.sidebar.title("📌 Menú de Control")
menu = st.sidebar.selectbox("Selecciona una opción", [
    "📝 Registrar Sesión / Ficha Semanal", 
    "📊 Cuadro Resumen y Progreso", 
    "👥 Gestión de Opositores y Perfiles",
    "📊 Histórico y Exportación por Alumno"
])

if menu == "📝 Registrar Sesión / Ficha Semanal":
    st.subheader("📝 Ficha de Seguimiento y Control Semanal")
    
    if not lista_alumnos:
        st.warning("No hay alumnos registrados.")
    else:
        with st.form("form_lectura"):
            col1, col2 = st.columns(2)
            with col1:
                alumno_sel = st.selectbox("Opositor", lista_alumnos)
                bloque_sel = st.selectbox("Bloque de Materia", bloques_oposition)
                estado_semaforo = st.selectbox("Semáforo de Estado", ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"])
            with col2:
                fecha_sel = st.date_input("Fecha de Sesión", datetime.today())
                temas_semana = st.text_input("Temas que lleva para esta semana (Ej: Temas 5 al 9)")
                tema_escrito = st.text_input("Tema escrito / Insaculado en clase (Opcional)")
                
            tiempo_redaccion = st.slider("Tiempo empleado en exposición/redacción (minutos)", 30, 90, 60)
            
            errores = st.multiselect("Etiquetas de Errores Recurrentes detectados", [
                "[E] Fallo de Estructura / Índice", 
                "[N] Error Normativo / Plazos", 
                "[T] Problemas de Gestión del Tiempo", 
                "[S] Falta de Síntesis"
            ])
            
            feedback = st.text_area(
                "Diagnóstico Cualitativo", 
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
                    "Estado_Semaforo": [estado_semaforo],
                    "Errores_Frecuentes": [", ".join(errores)],
                    "Feedback_Cualitativo": [feedback]
                })
                
                df_seguimiento = pd.concat([df_seguimiento, nuevo_registro], ignore_index=True)
                df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success(f"¡Ficha guardada correctamente para {alumno_sel}!")

elif menu == "📊 Cuadro Resumen y Progreso":
    st.subheader("📊 Cuadro Resumen General de Progreso")
    
    if df_seguimiento.empty:
        st.info("Todavía no hay registros guardados.")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total de Sesiones Registradas", len(df_seguimiento))
        with col_m2:
            st.metric("Opositores con Actividad", df_seguimiento["Alumno"].nunique())
        
        st.markdown("### 📈 Actividad Total por Alumno")
        resumen_alumnos = df_seguimiento.groupby("Alumno").size().reset_index(name="Revisiones Totales")
        st.dataframe(resumen_alumnos, use_container_width=True)
        
        st.markdown("### 🧱 Cobertura por Bloques de Materia")
        resumen_bloques = df_seguimiento.groupby("Bloque").size().reset_index(name="Veces Practicado")
        st.dataframe(resumen_bloques, use_container_width=True)

elif menu == "👥 Gestión de Opositores y Perfiles":
    st.subheader("👥 Gestión de Alumnos y Edición de Perfiles")
    
    sub_opcion = st.radio("¿Qué deseas hacer?", ["Editar Perfil Existente", "Añadir Nuevo Opositor", "Eliminar Opositor"])
    
    if sub_opcion == "Editar Perfil Existente":
        st.markdown("### ✏️ Modificar Datos del Opositor")
        alumno_editar = st.selectbox("Selecciona opositor a editar", lista_alumnos)
        
        # Obtener datos actuales del alumno
        datos_actuales = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].iloc[0]
        
        with st.form("form_editar_alumno"):
            nuevo_nombre_val = st.text_input("Nombre y Apellidos", value=str(datos_actuales["Alumno"]))
            nuevo_tel_val = st.text_input("Teléfono de contacto", value=str(datos_actuales["Telefono"]) if pd.notna(datos_actuales["Telefono"]) else "")
            nuevo_correo_val = st.text_input("Correo electrónico", value=str(datos_actuales["Correo"]) if pd.notna(datos_actuales["Correo"]) else "")
            nuevas_circ = st.text_area("Circunstancias / Notas de perfil", value=str(datos_actuales["Circunstancias"]) if pd.notna(datos_actuales["Circunstancias"]) else "")
            
            guardar_cambios = st.form_submit_button("Guardar Cambios de Perfil")
            
            if guardar_cambios:
                # Actualizar el DataFrame de alumnos
                idx = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].index[0]
                df_alumnos_db.at[idx, "Alumno"] = nuevo_nombre_val
                df_alumnos_db.at[idx, "Telefono"] = nuevo_tel_val
                df_alumnos_db.at[idx, "Correo"] = nuevo_correo_val
                df_alumnos_db.at[idx, "Circunstancias"] = nuevas_circ
                guardar_alumnos(df_alumnos_db)
                
                # Actualizar también los registros históricos si cambió el nombre
                if alumno_editar != nuevo_nombre_val:
                    df_seguimiento.loc[df_seguimiento["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                    df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                
                st.success(f"¡Perfil de {nuevo_nombre_val} actualizado correctamente!")
                st.rerun()

    elif sub_opcion == "Añadir Nuevo Opositor":
        st.markdown("### ➕ Dar de Alta a un Opositor")
        with st.form("form_nuevo_alumno"):
            n_nombre = st.text_input("Nombre y Apellidos")
            n_tel = st.text_input("Teléfono")
            n_correo = st.text_input("Correo electrónico")
            n_circ = st.text_area("Circunstancias iniciales")
            
            btn_crear = st.form_submit_button("Crear Opositor")
            
            if btn_crear:
                if n_nombre and n_nombre not in lista_alumnos:
                    nuevo_fila = pd.DataFrame({
                        "Alumno": [n_nombre],
                        "Telefono": [n_tel],
                        "Correo": [n_correo],
                        "Circunstancias": [n_circ]
                    })
                    df_alumnos_db = pd.concat([df_alumnos_db, nuevo_fila], ignore_index=True)
                    guardar_alumnos(df_alumnos_db)
                    st.success(f"¡Opositor {n_nombre} añadido con éxito!")
                    st.rerun()
                else:
                    st.error("El nombre está vacío o ya existe en la lista.")

    elif sub_opcion == "Eliminar Opositor":
        st.markdown("### ❌ Dar de Baja a un Opositor")
        alumno_a_borrar = st.selectbox("Selecciona opositor a eliminar de la lista", lista_alumnos)
        if st.button("Eliminar Definitivamente"):
            if alumno_a_borrar in lista_alumnos:
                df_alumnos_db = df_alumnos_db[df_alumnos_db["Alumno"] != alumno_a_borrar]
                guardar_alumnos(df_alumnos_db)
                st.success(f"Se ha eliminado a {alumno_a_borrar}.")
                st.rerun()

elif menu == "📊 Histórico y Exportación por Alumno":
    st.subheader("📊 Histórico Individual y Exportación")
    
    if not lista_alumnos:
        st.info("No hay alumnos.")
    else:
        alumno_filtro = st.selectbox("Selecciona al opositor", lista_alumnos)
        
        # Mostrar datos del perfil en la cabecera del histórico
        perfil_info = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_filtro].iloc[0]
        st.info(f"📞 Teléfono: {perfil_info['Telefono'] or 'No especificado'} | ✉️ Correo: {perfil_info['Correo'] or 'No especificado'} | 📝 Circunstancias: {perfil_info['Circunstancias'] or 'Ninguna'}")
        
        df_alumno = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
        
        if not df_alumno.empty:
            st.metric(label="Total de registros del alumno", value=len(df_alumno))
            st.dataframe(df_alumno, use_container_width=True)
            
            csv_data = df_alumno.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Histórico del Alumno (CSV)",
                data=csv_data,
                file_name=f"historial_{alumno_filtro.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aún no hay registros de seguimiento guardados para este opositor.")
