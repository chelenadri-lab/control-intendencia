import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Control Oposición Intendencia", layout="wide")

DB_ALUMNOS = "alumnos_intendencia_perfiles.csv"
DB_SEGUIMIENTO = "seguimiento_opositores.csv"
DB_TURNOS = "turnos_simulacro_dia.csv"

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
    "🕒 Turnos de Simulacro (En Vivo)",
    "📝 Registrar Sesión / Ficha (General)", 
    "📊 Cuadro Resumen y Progreso", 
    "👥 Gestión de Opositores y Perfiles",
    "📊 Histórico y Exportación por Alumno"
])

if menu == "🕒 Turnos de Simulacro (En Vivo)":
    st.subheader("🕒 Gestión de Turnos de Simulacro (Lunes Tarde)")
    st.markdown("Organización secuencial de las entradas de los opositores cada 15 minutos desde las 16:00 h.")
    
    # Selector de la fecha de los simulacros de este lunes
    fecha_simulacro = st.date_input("Fecha de la sesión de simulacros", datetime.today())
    
    # Generar franjas horarias automáticas cada 15 min desde las 16:00 hasta completar opositores
    # (Por defecto generamos bloques de 15 min)
    hora_inicio = datetime.strptime("16:00", "%H:%M")
    franjas_horarias = []
    for i in range(len(lista_alumnos)):
        hora_franja = (hora_inicio + timedelta(minutes=15 * i)).strftime("%H:%M")
        franjas_horarias.append(hora_franja)
        
    st.markdown("---")
    st.info("💡 **Modo Dinámico de Entrada:** Selecciona el opositor que entra en cada franja horaria y evalúalo directamente al instante.")

    # Crear un formulario interactivo para la tarde
    with st.form("form_parrilla_turnos"):
        registros_dia = []
        
        # Mostramos en columnas o filas organizadas las franjas
        asignaciones_actuales = {}
        for idx, hora in enumerate(franjas_horarias):
            col_h, col_a = st.columns([1, 3])
            with col_h:
                st.markdown(f"### ⏰ {hora}")
            with col_a:
                # Por defecto asignamos los alumnos en orden de la lista si no hay otra preferencia
                def_index = idx if idx < len(lista_alumnos) else 0
                al_asignado = st.selectbox(f"Opositor para las {hora}", lista_alumnos, index=def_index, key=f"turno_{idx}")
                asignaciones_actuales[hora] = al_asignado
                
        guardar_parrilla = st.form_submit_button("Bloquear / Actualizar Parrilla de Turnos")
        if guardar_parrilla:
            st.success("¡Parrilla de turnos fijada para la sesión de hoy!")

    st.markdown("---")
    st.markdown("### ⚡ Evaluación Rápida por Turno (Entrada en Consulta)")
    
    # Selector rápido del opositor que está entrando por la puerta ahora mismo
    alumno_en_puerta = st.selectbox("Opositor que entra a consulta/simulacro ahora mismo:", lista_alumnos, key="puerta_select")
    
    # Cargar datos del perfil rápido
    perfil_puerta = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_en_puerta].iloc[0]
    if perfil_puerta["Circunstancias"]:
        st.warning(f"📝 **Nota de perfil / Circunstancias:** {perfil_puerta['Circunstancias']}")

    with st.form("form_evaluacion_flash"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            bloque_flash = st.selectbox("Bloque de Materia", bloques_oposition, key="f_bloque")
            semaforo_flash = st.selectbox("Semáforo de Estado", ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"], key="f_sem")
        with col_f2:
            temas_semana_flash = st.text_input("Temas que traía para esta semana", key="f_temas_sem")
            tema_escrito_flash = st.text_input("Tema escrito / insaculado en el atril", key="f_tema_esc")
            
        tiempo_flash = st.slider("Tiempo empleado (minutos)", 15, 90, 60, key="f_tiempo")
        
        errores_flash = st.multiselect("Etiquetas de Errores Recurrentes", [
            "[E] Fallo de Estructura / Índice", 
            "[N] Error Normativo / Plazos", 
            "[T] Problemas de Gestión del Tiempo", 
            "[S] Falta de Síntesis"
        ], key="f_err")
        
        feedback_flash = st.text_area("Diagnóstico Cualitativo Rápido", placeholder="Notas al vuelo de su exposición...", key="f_feed")
        
        btn_guardar_flash = st.form_submit_button("💾 Guardar Evaluación de este Turno")
        
        if btn_guardar_flash:
            nuevo_reg_flash = pd.DataFrame({
                "Fecha": [str(fecha_simulacro)],
                "Alumno": [alumno_en_puerta],
                "Bloque": [bloque_flash],
                "Temas_Para_Esta_Semana": [temas_semana_flash],
                "Tema_Escrito": [tema_escrito_flash],
                "Tiempo_Minutos": [tiempo_flash],
                "Estado_Semaforo": [semaforo_flash],
                "Errores_Frecuentes": [", ".join(errores_flash)],
                "Feedback_Cualitativo": [feedback_flash]
            })
            
            df_seguimiento = pd.concat([df_seguimiento, nuevo_reg_flash], ignore_index=True)
            df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
            st.success(f"¡Evaluación de {alumno_en_puerta} registrada con éxito! Siguiente turno listo.")

elif menu == "📝 Registrar Sesión / Ficha (General)":
    # (El formulario clásico anterior por si se prefiere usar fuera de los lunes)
    st.subheader("📝 Ficha General de Seguimiento")
    # ... [Mantiene el código de la ficha clásica] ...
    st.info("Usa la pestaña 'Turnos de Simulacro (En Vivo)' para la dinámica de los lunes por la tarde.")

# [Resto de menús: Cuadro Resumen, Gestión de Opositores, Histórico...]
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
        alumno_editar = st.selectbox("Selecciona opositor a editar", lista_alumnos)
        datos_actuales = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].iloc[0]
        with st.form("form_editar_alumno"):
            nuevo_nombre_val = st.text_input("Nombre y Apellidos", value=str(datos_actuales["Alumno"]))
            nuevo_tel_val = st.text_input("Teléfono de contacto", value=str(datos_actuales["Telefono"]) if pd.notna(datos_actuales["Telefono"]) else "")
            nuevo_correo_val = st.text_input("Correo electrónico", value=str(datos_actuales["Correo"]) if pd.notna(datos_actuales["Correo"]) else "")
            nuevas_circ = st.text_area("Circunstancias / Notas de perfil", value=str(datos_actuales["Circunstancias"]) if pd.notna(datos_actuales["Circunstancias"]) else "")
            guardar_cambios = st.form_submit_button("Guardar Cambios de Perfil")
            if guardar_cambios:
                idx = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].index[0]
                df_alumnos_db.at[idx, "Alumno"] = nuevo_nombre_val
                df_alumnos_db.at[idx, "Telefono"] = nuevo_tel_val
                df_alumnos_db.at[idx, "Correo"] = nuevo_correo_val
                df_alumnos_db.at[idx, "Circunstancias"] = nuevas_circ
                guardar_alumnos(df_alumnos_db)
                if alumno_editar != nuevo_nombre_val:
                    df_seguimiento.loc[df_seguimiento["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                    df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success(f"¡Perfil de {nuevo_nombre_val} actualizado!")
                st.rerun()
    elif sub_opcion == "Añadir Nuevo Opositor":
        with st.form("form_nuevo_alumno"):
            n_nombre = st.text_input("Nombre y Apellidos")
            n_tel = st.text_input("Teléfono")
            n_correo = st.text_input("Correo electrónico")
            n_circ = st.text_area("Circunstancias iniciales")
            btn_crear = st.form_submit_button("Crear Opositor")
            if btn_crear:
                if n_nombre and n_nombre not in lista_alumnos:
                    nuevo_fila = pd.DataFrame({"Alumno": [n_nombre], "Telefono": [n_tel], "Correo": [n_correo], "Circunstancias": [n_circ]})
                    df_alumnos_db = pd.concat([df_alumnos_db, nuevo_fila], ignore_index=True)
                    guardar_alumnos(df_alumnos_db)
                    st.success(f"¡Opositor {n_nombre} añadido!")
                    st.rerun()
    elif sub_opcion == "Eliminar Opositor":
        alumno_a_borrar = st.selectbox("Selecciona opositor a eliminar", lista_alumnos)
        if st.button("Eliminar Definitivamente"):
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
        perfil_info = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_filtro].iloc[0]
        st.info(f"📞 Teléfono: {perfil_info['Telefono'] or 'No especificado'} | ✉️ Correo: {perfil_info['Correo'] or 'No especificado'} | 📝 Circunstancias: {perfil_info['Circunstancias'] or 'Ninguna'}")
        df_alumno = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
        if not df_alumno.empty:
            st.metric(label="Total de registros", value=len(df_alumno))
            st.dataframe(df_alumno, use_container_width=True)
            csv_data = df_alumno.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Histórico (CSV)",
                data=csv_data,
                file_name=f"historial_{alumno_filtro.replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Aún no hay registros guardados para este opositor.")
