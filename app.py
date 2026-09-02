import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

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

def cargar_alumnos():
    if os.path.exists(DB_ALUMNOS):
        df = pd.read_csv(DB_ALUMNOS)
        for col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "")
        return df
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

def parsear_temas(texto_temas):
    """Convierte textos como '6-10' o '1, 3, 5' en una lista de números de temas únicos."""
    if not isinstance(texto_temas, str) or not texto_temas.strip() or texto_temas.strip() == "nan":
        return set()
    
    temas_set = set()
    partes = texto_temas.split(",")
    for parte in partes:
        parte = parte.strip()
        if "-" in parte:
            try:
                inicio, fin = map(int, parte.split("-"))
                if inicio <= fin:
                    temas_set.update(range(inicio, fin + 1))
            except ValueError:
                pass
        else:
            try:
                temas_set.add(int(parte))
            except ValueError:
                pass
    return temas_set

df_alumnos_db = cargar_alumnos()
lista_alumnos = df_alumnos_db["Alumno"].tolist()
df_seguimiento = cargar_seguimiento()

st.sidebar.title("📌 Menú de Control")
menu = st.sidebar.selectbox("Selecciona una opción", [
    "🕒 Turnos de Simulacro (En Vivo)",
    "📝 Registrar Sesión / Ficha (General)", 
    "📊 Cuadro Resumen y Progreso", 
    "👥 Gestión de Opositores y Perfiles",
    "📊 Histórico, Bloques y Desviación"
])

if menu == "🕒 Turnos de Simulacro (En Vivo)":
    st.subheader("🕒 Gestión de Turnos de Simulacro (Lunes Tarde)")
    fecha_simulacro = st.date_input("Fecha de la sesión de simulacros", datetime.today())
    
    hora_inicio = datetime.strptime("16:00", "%H:%M")
    franjas_horarias = []
    for i in range(len(lista_alumnos)):
        franjas_horarias.append((hora_inicio + timedelta(minutes=15 * i)).strftime("%H:%M"))
        
    st.markdown("---")
    with st.form("form_parrilla_turnos"):
        for idx, hora in enumerate(franjas_horarias):
            col_h, col_a = st.columns([1, 3])
            with col_h:
                st.markdown(f"### ⏰ {hora}")
            with col_a:
                st.selectbox(f"Opositor para las {hora}", lista_alumnos, index=idx if idx < len(lista_alumnos) else 0, key=f"turno_{idx}")
        if st.form_submit_button("Bloquear / Actualizar Parrilla de Turnos"):
            st.success("¡Parrilla fijada!")

    st.markdown("---")
    st.markdown("### ⚡ Evaluación Rápida por Turno (Entrada en Consulta)")
    
    if lista_alumnos:
        alumno_en_puerta = st.selectbox("Opositor que entra a consulta ahora mismo:", lista_alumnos, key="puerta_select")
        perfil_puerta = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_en_puerta]
        if not perfil_puerta.empty and perfil_puerta.iloc[0]["Circunstancias"] and perfil_puerta.iloc[0]["Circunstancias"] != "nan":
            st.warning(f"📝 **Circunstancias:** {perfil_puerta.iloc[0]['Circunstancias']}")

        with st.form("form_evaluacion_flash"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                bloque_flash = st.selectbox("Bloque de Materia", bloques_oposition, key="f_bloque")
                semaforo_flash = st.selectbox("Semáforo de Estado", ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"], key="f_sem")
            with col_f2:
                temas_semana_flash = st.text_input("Temas traídos esta semana (ej. 6-10 o 1,3,5)", key="f_temas_sem")
                tema_escrito_flash = st.text_input("Tema escrito / insaculado en el atril", key="f_tema_esc")
                
            tiempo_flash = st.slider("Tiempo empleado (minutos)", 15, 90, 60, key="f_tiempo")
            errores_flash = st.multiselect("Etiquetas de Errores", ["[E] Estructura", "[N] Normativa", "[T] Tiempo", "[S] Síntesis"], key="f_err")
            feedback_flash = st.text_area("Diagnóstico Cualitativo", key="f_feed")
            
            if st.form_submit_button("💾 Guardar Evaluación"):
                nuevo_reg = pd.DataFrame({
                    "Fecha": [str(fecha_simulacro)], "Alumno": [alumno_en_puerta], "Bloque": [bloque_flash],
                    "Temas_Para_Esta_Semana": [temas_semana_flash], "Tema_Escrito": [tema_escrito_flash],
                    "Tiempo_Minutos": [tiempo_flash], "Estado_Semaforo": [semaforo_flash],
                    "Errores_Frecuentes": [", ".join(errores_flash)], "Feedback_Cualitativo": [feedback_flash]
                })
                df_seguimiento = pd.concat([df_seguimiento, nuevo_reg], ignore_index=True)
                df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success(f"¡Evaluación de {alumno_en_puerta} guardada!")

elif menu == "📝 Registrar Sesión / Ficha (General)":
    st.subheader("📝 Ficha General de Seguimiento")
    if lista_alumnos:
        with st.form("form_general"):
            al_gen = st.selectbox("Opositor", lista_alumnos, key="g_al")
            bl_gen = st.selectbox("Bloque", bloques_oposition, key="g_bl")
            sem_gen = st.selectbox("Estado", ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"], key="g_sem")
            f_gen = st.date_input("Fecha", datetime.today(), key="g_f")
            t_sem_gen = st.text_input("Temas de la semana (ej. 1-5)", key="g_tsem")
            t_esc_gen = st.text_input("Tema escrito", key="g_tesc")
            t_min_gen = st.slider("Minutos", 30, 90, 60, key="g_tmin")
            err_gen = st.multiselect("Errores", ["[E] Estructura", "[N] Normativa", "[T] Tiempo", "[S] Síntesis"], key="g_err")
            feed_gen = st.text_area("Feedback", key="g_feed")
            
            if st.form_submit_button("Guardar"):
                reg_gen = pd.DataFrame({
                    "Fecha": [str(f_gen)], "Alumno": [al_gen], "Bloque": [bl_gen], 
                    "Temas_Para_Esta_Semana": [t_sem_gen], "Tema_Escrito": [t_esc_gen], 
                    "Tiempo_Minutos": [t_min_gen], "Estado_Semaforo": [sem_gen], 
                    "Errores_Frecuentes": [", ".join(err_gen)], "Feedback_Cualitativo": [feed_gen]
                })
                df_seguimiento = pd.concat([df_seguimiento, reg_gen], ignore_index=True)
                df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success("Guardado correctamente.")

elif menu == "📊 Cuadro Resumen y Progreso":
    st.subheader("📊 Cuadro Resumen General de Progreso y Bloques")
    if df_seguimiento.empty:
        st.info("Todavía no hay registros guardados.")
    else:
        st.markdown("### 🧱 Cobertura y Temas Vistos por Alumno y Bloque")
        # Procesar los temas vistos por bloque para cada alumno
        resumen_data = []
        for alumno in lista_alumnos:
            df_al = df_seguimiento[df_seguimiento["Alumno"] == alumno]
            for bloque in bloques_oposition:
                df_bloque = df_al[df_al["Bloque"] == bloque]
                temas_totales_set = set()
                for _, row in df_bloque.iterrows():
                    temas_totales_set.update(parsear_temas(str(row["Temas_Para_Esta_Semana"])))
                
                # Formatear la lista de temas vistos de forma ordenada
                lista_ordenada = sorted(list(temas_totales_set))
                temas_str = ", ".join(map(str, lista_ordenada)) if lista_ordenada else "Ninguno"
                
                resumen_data.append({
                    "Alumno": alumno,
                    "Bloque": bloque,
                    "Nº Temas Vistos": len(temas_totales_set),
                    "Temas Abordados": temas_str
                })
        
        df_resumen_bloques = pd.DataFrame(resumen_data)
        st.dataframe(df_resumen_bloques, use_container_width=True)

elif menu == "👥 Gestión de Opositores y Perfiles":
    st.subheader("👥 Gestión de Alumnos y Perfiles")
    if not lista_alumnos:
        sub_opcion = "Añadir Nuevo Opositor"
    else:
        sub_opcion = st.radio("¿Qué deseas hacer?", ["Editar Perfil Existente", "Añadir Nuevo Opositor", "Eliminar Opositor"])
    
    if sub_opcion == "Editar Perfil Existente" and lista_alumnos:
        alumno_editar = st.selectbox("Selecciona opositor", lista_alumnos)
        datos_actuales = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].iloc[0]
        with st.form("form_editar_alumno"):
            nuevo_nombre_val = st.text_input("Nombre y Apellidos", value=str(datos_actuales["Alumno"]))
            nuevo_tel_val = st.text_input("Teléfono", value=str(datos_actuales["Telefono"]))
            nuevo_correo_val = st.text_input("Correo", value=str(datos_actuales["Correo"]))
            nuevas_circ = st.text_area("Circunstancias", value=str(datos_actuales["Circunstancias"]))
            
            if st.form_submit_button("Guardar Cambios"):
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Telefono"] = nuevo_tel_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Correo"] = nuevo_correo_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Circunstancias"] = nuevas_circ
                guardar_alumnos(df_alumnos_db)
                if alumno_editar != nuevo_nombre_val:
                    df_seguimiento.loc[df_seguimiento["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                    df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success("¡Actualizado!")
                st.rerun()
    elif sub_opcion == "Añadir Nuevo Opositor":
        with st.form("form_nuevo_alumno"):
            n_nombre = st.text_input("Nombre y Apellidos")
            n_tel = st.text_input("Teléfono")
            n_correo = st.text_input("Correo")
            n_circ = st.text_area("Circunstancias")
            if st.form_submit_button("Crear"):
                if n_nombre and n_nombre not in lista_alumnos:
                    nuevo_fila = pd.DataFrame({"Alumno": [n_nombre], "Telefono": [n_tel], "Correo": [n_correo], "Circunstancias": [n_circ]})
                    df_alumnos_db = pd.concat([df_alumnos_db, nuevo_fila], ignore_index=True)
                    guardar_alumnos(df_alumnos_db)
                    st.success("¡Añadido!")
                    st.rerun()
    elif sub_opcion == "Eliminar Opositor" and lista_alumnos:
        alumno_a_borrar = st.selectbox("Selecciona opositor", lista_alumnos)
        if st.button("Eliminar Definitivamente"):
            df_alumnos_db = df_alumnos_db[df_alumnos_db["Alumno"] != alumno_a_borrar]
            guardar_alumnos(df_alumnos_db)
            st.success("Eliminado.")
            st.rerun()

elif menu == "📊 Histórico, Bloques y Desviación":
    st.subheader("📊 Histórico Individual, Desglose de Temas y Retraso Teórico")
    if not lista_alumnos:
        st.info("No hay alumnos.")
    else:
        alumno_filtro = st.selectbox("Selecciona al opositor", lista_alumnos)
        perfil_info = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_filtro]
        if not perfil_info.empty:
            p = perfil_info.iloc[0]
            st.info(f"📞 Teléfono: {p['Telefono']} | ✉️ Correo: {p['Correo']} | 📝 Circunstancias: {p['Circunstancias']}")
        
        st.markdown("---")
        st.markdown("### 🧱 Detalle por Bloque de este Alunmno")
        df_al_seg = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
        
        detalle_bloques = []
        for bloque in bloques_oposition:
            df_b = df_al_seg[df_al_seg["Bloque"] == bloque]
            temas_b = set()
            for _, r in df_b.iterrows():
                temas_b.update(parsear_temas(str(r["Temas_Para_Esta_Semana"])))
            lista_t = sorted(list(temas_b))
            detalle_bloques.append({
                "Bloque": bloque,
                "Total Temas Vistos": len(temas_b),
                "Temas Concretos Estudiados": ", ".join(map(str, lista_t)) if lista_t else "Ninguno"
            })
        st.dataframe(pd.DataFrame(detalle_bloques), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### ⏱️ Control de Desviación con el Calendario Teórico")
        # Cálculo orientativo de semanas de retraso estimado comparado con el avance real
        total_temas_estudiados_alumno = sum(d["Total Temas Vistos"] for d in detalle_bloques)
        
        # Suposición estándar de ritmo teórico (ej. 5 temas por semana de media en la planificación)
        TEMAS_TEORICOS_SEMANA_MEDIA = 5 
        # Semanas transcurridas desde el inicio estimado o número de sesiones registradas como referencia
        semanas_registradas = max(len(df_al_seg), 1)
        temas_esperados_teoricos = semanas_registradas * TEMAS_TEORICOS_SEMANA_MEDIA
        
        diferencia_temas = temas_esperados_teoricos - total_temas_estudiados_alumno
        semanas_retraso = round(diferencia_temas / TEMAS_TEORICOS_SEMANA_MEDIA, 1)
        
        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.metric("Temas Acumulados Vistos", total_temas_estudiados_alumno)
        col_d2.metric("Temas Teóricos Esperados", temas_esperados_teoricos)
        if semanas_retraso > 0:
            col_d3.metric("Desviación Estimada", f"+{semanas_retraso} semanas de retraso", delta_color="inverse")
        else:
            col_d3.metric("Desviación Estimada", "Al día o adelantado", delta_color="normal")

        st.markdown("---")
        st.markdown("### 📋 Registro Histórico Detallado")
        if not df_al_seg.empty:
            st.dataframe(df_al_seg, use_container_width=True)
            csv_data = df_al_seg.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Histórico (CSV)", data=csv_data, file_name=f"historial_{alumno_filtro.replace(' ', '_')}.csv", mime="text/csv")
        else:
            st.info("Aún no hay registros guardados para este opositor.")
