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

opciones_asistencia = ["Asiste", "Justificado (Estudio / Test)", "Falta Injustificada"]

# Franjas de 15 minutos de la tarde ampliadas hasta las 21:30
FRANJAS_HORARIAS_POSIBLES = [
    "16:00", "16:15", "16:30", "16:45",
    "17:00", "17:15", "17:30", "17:45",
    "18:00", "18:15", "18:30", "18:45",
    "19:00", "19:15", "19:30", "19:45",
    "20:00", "20:15", "20:30", "20:45",
    "21:00", "21:15", "21:30"
]

def cargar_alumnos():
    if os.path.exists(DB_ALUMNOS):
        df = pd.read_csv(DB_ALUMNOS)
        if "Asiste_Por_Defecto" not in df.columns:
            df["Asiste_Por_Defecto"] = True
        if "Franja_Defecto" not in df.columns:
            df["Franja_Defecto"] = ",".join(FRANJAS_HORARIAS_POSIBLES)
            
        for col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "")
        df["Asiste_Por_Defecto"] = df["Asiste_Por_Defecto"].apply(lambda x: True if str(x).lower() in ["true", "1", "yes"] else False)
        return df
    else:
        df = pd.DataFrame({
            "Alumno": ALUMNOS_INICIALES,
            "Telefono": ["" for _ in ALUMNOS_INICIALES],
            "Correo": ["" for _ in ALUMNOS_INICIALES],
            "Circunstancias": ["" for _ in ALUMNOS_INICIALES],
            "Asiste_Por_Defecto": [True for _ in ALUMNOS_INICIALES],
            "Franja_Defecto": [",".join(FRANJAS_HORARIAS_POSIBLES) for _ in ALUMNOS_INICIALES]
        })
        df.to_csv(DB_ALUMNOS, index=False)
        return df

def guardar_alumnos(df):
    df.to_csv(DB_ALUMNOS, index=False)

def cargar_seguimiento():
    if os.path.exists(DB_SEGUIMIENTO):
        df = pd.read_csv(DB_SEGUIMIENTO)
        if "Asistencia" not in df.columns:
            df["Asistencia"] = "Asiste"
        return df
    else:
        df_inicial = pd.DataFrame(columns=[
            "Fecha", "Alumno", "Bloque", "Asistencia", "Temas_Para_Esta_Semana", 
            "Tema_Escrito", "Tiempo_Minutos", "Estado_Semaforo", 
            "Errores_Frecuentes", "Feedback_Cualitativo"
        ])
        df_inicial.to_csv(DB_SEGUIMIENTO, index=False)
        return df_inicial

def parsear_temas(texto_temas):
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
    "📊 Cuadro Resumen y Progreso", 
    "📅 Control y Edición de Sesiones",
    "👥 Gestión de Opositores y Perfiles",
    "📊 Histórico, Bloques y Desviación"
])

if menu == "🕒 Turnos de Simulacro (En Vivo)":
    st.subheader("🕒 Gestión y Planificación de Turnos de Simulacro (Lunes Tarde)")
    fecha_simulacro = st.date_input("Fecha de la sesión de simulacros", datetime.today())
    
    st.markdown("---")
    st.markdown("### 🛠️ Paso 1: Configuración Previa y Asistencia de la Sesión")
    st.info("Indica para cada alumno su asistencia, bloque de materia y revisa su disponibilidad de 15 minutos en esta convocatoria.")

    with st.form("form_configuracion_sesion"):
        configuracion_alumnos = {}
        
        for alumno in lista_alumnos:
            row_al = df_alumnos_db[df_alumnos_db["Alumno"] == alumno].iloc[0]
            def_asiste = bool(row_al["Asiste_Por_Defecto"])
            estado_asis_inicial = "Asiste" if def_asiste else "Falta Injustificada"
            
            franjas_str = str(row_al["Franja_Defecto"])
            franjas_guardadas = [f.strip() for f in franjas_str.split(",") if f.strip()]
            
            with st.expander(f"👤 {alumno}"):
                col_c1, col_c2 = st.columns([1.5, 2])
                with col_c1:
                    estado_asis = st.selectbox("Asistencia", opciones_asistencia, index=opciones_asistencia.index(estado_asis_inicial), key=f"asis_{alumno}")
                    bloque_rapido = st.selectbox("Bloque habitual", bloques_oposition, key=f"bl_rap_{alumno}")
                with col_c2:
                    st.markdown("**Disponibilidad horaria (15 min):**")
                    cols_f = st.columns(4)
                    franjas_sesion_seleccionadas = []
                    for idx_f, hora_f in enumerate(FRANJAS_HORARIAS_POSIBLES):
                        default_val = hora_f in franjas_guardadas
                        with cols_f[idx_f % 4]:
                            if st.checkbox(hora_f, value=default_val, key=f"ses_f_{alumno}_{hora_f}"):
                                franjas_sesion_seleccionadas.append(hora_f)
                
                configuracion_alumnos[alumno] = {
                    "asistencia": estado_asis,
                    "bloque": bloque_rapido,
                    "franjas": franjas_sesion_seleccionadas
                }
        
        actualizar_permanentes = st.checkbox("💾 Actualizar también las disponibilidades y asistencias permanentes en los perfiles con estos cambios", value=False)
        btn_generar_parrilla = st.form_submit_button("⚙️ Generar y Bloquear Parrilla de Turnos Automática")

        if btn_generar_parrilla:
            for al, cfg in configuracion_alumnos.items():
                if actualizar_permanentes:
                    es_asiste_bool = True if cfg["asistencia"] == "Asiste" else False
                    df_alumnos_db.loc[df_alumnos_db["Alumno"] == al, "Asiste_Por_Defecto"] = es_asiste_bool
                    df_alumnos_db.loc[df_alumnos_db["Alumno"] == al, "Franja_Defecto"] = ",".join(cfg["franjas"])
            if actualizar_permanentes:
                guardar_alumnos(df_alumnos_db)
            
            for al, cfg in configuracion_alumnos.items():
                nuevo_reg = pd.DataFrame({
                    "Fecha": [str(fecha_simulacro)], "Alumno": [al], "Bloque": [cfg["bloque"]],
                    "Asistencia": [cfg["asistencia"]], "Temas_Para_Esta_Semana": [""], 
                    "Tema_Escrito": [""], "Tiempo_Minutos": [0], 
                    "Estado_Semaforo": ["🟢 Consolidado / Vivo"], "Errores_Frecuentes": [""], 
                    "Feedback_Cualitativo": ["Generado automáticamente desde planificación."]
                })
                df_seguimiento = pd.concat([df_seguimiento, nuevo_reg], ignore_index=True)
            df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
            st.toast("¡Parrilla generada y registros de asistencia guardados!", icon="✅")

    st.markdown("---")
    st.markdown("### ⏰ Paso 2: Parrilla de Entradas (Cada 15 min desde las 16:00)")
    
    alumnos_asistentes = [al for al, cfg in configuracion_alumnos.items() if cfg["asistencia"] == "Asiste"]
    
    if not alumnos_asistentes:
        st.warning("No hay alumnos marcados como asistentes presenciales para esta sesión.")
    else:
        hora_inicio = datetime.strptime("16:00", "%H:%M")
        franjas_horarias = []
        for i in range(len(alumnos_asistentes)):
            franjas_horarias.append((hora_inicio + timedelta(minutes=15 * i)).strftime("%H:%M"))
        
        with st.form("form_ver_parrilla"):
            for idx, hora in enumerate(franjas_horarias):
                col_h, col_a, col_t = st.columns([1, 2, 1])
                with col_h:
                    st.markdown(f"### ⏰ {hora}")
                with col_a:
                    def_al = alumnos_asistentes[0]
                    candidatos_disponibles = [a for a in alumnos_asistentes if hora in configuracion_alumnos[a]["franjas"]]
                    if candidatos_disponibles:
                        def_al = candidatos_disponibles[idx % len(candidatos_disponibles)]
                    else:
                        def_al = alumnos_asistentes[idx % len(alumnos_asistentes)]

                    st.selectbox(f"Opositor a las {hora}", alumnos_asistentes, index=alumnos_asistentes.index(def_al), key=f"parrilla_al_{idx}")
                with col_t:
                    st.markdown(f"**Prueba:** `Lectura Tema Escrito`")
                
            if st.form_submit_button("💾 Guardar Parrilla Definitiva"):
                st.success("¡Parrilla de la tarde fijada correctamente!")

    st.markdown("---")
    st.markdown("### ⚡ Paso 3: Actualizar Evaluación Detallada en Consulta")
    
    if lista_alumnos:
        alumno_en_puerta = st.selectbox("Opositor que entra a consulta:", lista_alumnos, key="puerta_select")
        perfil_puerta = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_en_puerta]
        if not perfil_puerta.empty and perfil_puerta.iloc[0]["Circunstancias"] and perfil_puerta.iloc[0]["Circunstancias"] != "nan":
            st.warning(f"📝 **Circunstancias:** {perfil_puerta.iloc[0]['Circunstancias']}")

        with st.form("form_evaluacion_flash"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                bloque_flash = st.selectbox("Bloque de Materia", bloques_oposition, key="f_bloque")
                asistencia_flash = st.selectbox("Control de Asistencia", opciones_asistencia, key="f_asis")
            with col_f2:
                semaforo_flash = st.selectbox("Semáforo de Estado", ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"], key="f_sem")
                
            temas_semana_flash = st.text_input("Temas traídos esta semana (ej. 6-10 o 1,3,5)", key="f_temas_sem")
            tema_escrito_flash = st.text_input("Tema escrito / insaculado en el atril", key="f_tema_esc")
            
            tiempo_flash = st.slider("Tiempo empleado (minutos)", 15, 90, 60, key="f_tiempo")
            errores_flash = st.multiselect("Etiquetas de Errores", ["[E] Estructura", "[N] Normativa", "[T] Tiempo", "[S] Síntesis"], key="f_err")
            feedback_flash = st.text_area("Diagnóstico Cualitativo", key="f_feed")
            
            if st.form_submit_button("💾 Guardar Evaluación de este Turno"):
                nuevo_reg = pd.DataFrame({
                    "Fecha": [str(fecha_simulacro)], "Alumno": [alumno_en_puerta], "Bloque": [bloque_flash],
                    "Asistencia": [asistencia_flash], "Temas_Para_Esta_Semana": [temas_semana_flash], 
                    "Tema_Escrito": [tema_escrito_flash], "Tiempo_Minutos": [tiempo_flash], 
                    "Estado_Semaforo": [semaforo_flash], "Errores_Frecuentes": [", ".join(errores_flash)], 
                    "Feedback_Cualitativo": [feedback_flash]
                })
                df_seguimiento = pd.concat([df_seguimiento, nuevo_reg], ignore_index=True)
                df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success(f"¡Evaluación de {alumno_en_puerta} guardada con éxito!")

elif menu == "📊 Cuadro Resumen y Progreso":
    st.subheader("📊 Cuadro Resumen Global por Opositor")
    if df_seguimiento.empty:
        st.info("Todavía no hay registros guardados.")
    else:
        st.markdown("### 📋 Matriz General de Avance (Ordenada de Mejor a Peor Progreso)")
        matriz_data = []
        for alumno in lista_alumnos:
            fila = {"Opositor": alumno}
            df_al = df_seguimiento[df_seguimiento["Alumno"] == alumno]
            
            total_faltas_inj_alumno = 0
            total_temas_alumno = 0
            
            for bloque in bloques_oposition:
                df_bloque = df_al[df_al["Bloque"] == bloque]
                temas_totales_set = set()
                
                for _, row in df_bloque.iterrows():
                    asis = str(row.get("Asistencia", "Asiste"))
                    if asis == "Falta Injustificada":
                        total_faltas_inj_alumno += 1
                    else:
                        temas_totales_set.update(parsear_temas(str(row["Temas_Para_Esta_Semana"])))
                
                num_temas_bloque = len(temas_totales_set)
                total_temas_alumno += num_temas_bloque
                
                lista_ordenada = sorted(list(temas_totales_set))
                detalle_str = f"({num_temas_bloque} temas)"
                if lista_ordenada:
                    detalle_str += f" [{', '.join(map(str, lista_ordenada))}]"
                
                fila[bloque] = detalle_str
                
            fila["❌ Faltas Injustificadas"] = total_faltas_inj_alumno
            score_progreso = total_temas_alumno - (total_faltas_inj_alumno * 5)
            fila["_score"] = score_progreso
            
            matriz_data.append(fila)
        
        df_matriz = pd.DataFrame(matriz_data)
        df_matriz = df_matriz.sort_values(by="_score", ascending=False).drop(columns=["_score"]).reset_index(drop=True)
        
        st.dataframe(df_matriz, use_container_width=True)

elif menu == "📅 Control y Edición de Sesiones":
    st.subheader("📅 Control, Modificación y Eliminación de Sesiones")
    if df_seguimiento.empty:
        st.info("No hay sesiones registradas.")
    else:
        df_ordenado = df_seguimiento.sort_values(by="Fecha", ascending=False).reset_index(drop=True)
        
        st.markdown("### Listado Completo de Sesiones Registradas")
        st.info("Selecciona el índice de la sesión que deseas editar o eliminar.")
        
        for idx, row in df_ordenado.iterrows():
            with st.expander(f"📅 Fecha: {row['Fecha']} | 👤 {row['Alumno']} | 🧱 {row['Bloque']} | 📌 {row['Asistencia']}"):
                with st.form(f"form_edit_sesion_{idx}"):
                    e_fecha = st.date_input("Fecha", value=datetime.strptime(str(row['Fecha']), "%Y-%m-%d").date() if "-" in str(row['Fecha']) else datetime.today(), key=f"ef_{idx}")
                    e_alumno = st.selectbox("Alumno", lista_alumnos, index=lista_alumnos.index(row['Alumno']) if row['Alumno'] in lista_alumnos else 0, key=f"eal_{idx}")
                    e_bloque = st.selectbox("Bloque", bloques_oposition, index=bloques_oposition.index(row['Bloque']) if row['Bloque'] in bloques_oposition else 0, key=f"ebl_{idx}")
                    
                    asis_actual = str(row['Asistencia'])
                    idx_asis = opciones_asistencia.index(asis_actual) if asis_actual in opciones_asistencia else 0
                    e_asistencia = st.selectbox("Asistencia", opciones_asistencia, index=idx_asis, key=f"easis_{idx}")
                    
                    e_temas = st.text_input("Temas", value=str(row['Temas_Para_Esta_Semana']), key=f"etemas_{idx}")
                    e_escrito = st.text_input("Tema Escrito", value=str(row['Tema_Escrito']), key=f"eesc_{idx}")
                    e_tiempo = st.slider("Minutos", 15, 90, int(row['Tiempo_Minutos']) if pd.notnull(row['Tiempo_Minutos']) and str(row['Tiempo_Minutos']).isdigit() else 60, key=f"etiemp_{idx}")
                    
                    sem_actual = str(row['Estado_Semaforo'])
                    opciones_sem = ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"]
                    idx_sem = opciones_sem.index(sem_actual) if sem_actual in opciones_sem else 0
                    e_semaforo = st.selectbox("Semáforo", opciones_sem, index=idx_sem, key=f"esem_{idx}")
                    
                    e_feedback = st.text_area("Feedback", value=str(row['Feedback_Cualitativo']), key=f"efeed_{idx}")
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        btn_guardar_cambios = st.form_submit_button("💾 Guardar Cambios")
                    with col_b2:
                        btn_borrar_sesion = st.form_submit_button("🗑️ Eliminar esta Sesión")
                        
                    if btn_guardar_cambios:
                        orig_idx = df_seguimiento[(df_seguimiento['Fecha'] == row['Fecha']) & 
                                                  (df_seguimiento['Alumno'] == row['Alumno']) & 
                                                  (df_seguimiento['Bloque'] == row['Bloque'])].index
                        if not orig_idx.empty:
                            i_real = orig_idx[0]
                            df_seguimiento.loc[i_real, 'Fecha'] = str(e_fecha)
                            df_seguimiento.loc[i_real, 'Alumno'] = e_alumno
                            df_seguimiento.loc[i_real, 'Bloque'] = e_bloque
                            df_seguimiento.loc[i_real, 'Asistencia'] = e_asistencia
                            df_seguimiento.loc[i_real, 'Temas_Para_Esta_Semana'] = e_temas
                            df_seguimiento.loc[i_real, 'Tema_Escrito'] = e_escrito
                            df_seguimiento.loc[i_real, 'Tiempo_Minutos'] = e_tiempo
                            df_seguimiento.loc[i_real, 'Estado_Semaforo'] = e_semaforo
                            df_seguimiento.loc[i_real, 'Feedback_Cualitativo'] = e_feedback
                            
                            df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                            st.success("¡Sesión actualizada correctamente!")
                            st.rerun()
                            
                    if btn_borrar_sesion:
                        orig_idx = df_seguimiento[(df_seguimiento['Fecha'] == row['Fecha']) & 
                                                  (df_seguimiento['Alumno'] == row['Alumno']) & 
                                                  (df_seguimiento['Bloque'] == row['Bloque'])].index
                        if not orig_idx.empty:
                            df_seguimiento = df_seguimiento.drop(orig_idx).reset_index(drop=True)
                            df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                            st.success("¡Sesión eliminada correctamente!")
                            st.rerun()

elif menu == "👥 Gestión de Opositores y Perfiles":
    st.subheader("👥 Gestión de Alumnos y Perfiles")
    if not lista_alumnos:
        sub_opcion = "Añadir Nuevo Opositor"
    else:
        sub_opcion = st.radio("¿Qué deseas hacer?", ["Editar Perfil Existente", "Añadir Nuevo Opositor", "Eliminar Opositor"])

    if sub_opcion == "Editar Perfil Existente" and lista_alumnos:
        alumno_editar = st.selectbox("Selecciona opositor", lista_alumnos)
        datos_actuales = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].iloc[0]
        
        franjas_str_act = str(datos_actuales["Franja_Defecto"])
        franjas_guardadas_act = [f.strip() for f in franjas_str_act.split(",") if f.strip()]
        
        with st.form("form_editar_alumno"):
            nuevo_nombre_val = st.text_input("Nombre y Apellidos", value=str(datos_actuales["Alumno"]))
            nuevo_tel_val = st.text_input("Teléfono", value=str(datos_actuales["Telefono"]))
            nuevo_correo_val = st.text_input("Correo", value=str(datos_actuales["Correo"]))
            nuevas_circ = st.text_area("Circunstancias", value=str(datos_actuales["Circunstancias"]))
            
            st.markdown("#### ⚙️ Preferencias Permanentes de Simulacro")
            val_asiste_def = bool(datos_actuales["Asiste_Por_Defecto"])
            nuevo_asiste_def = st.checkbox("Asiste por defecto cada semana", value=val_asiste_def)
            
            st.markdown("**Disponibilidad por franjas de 15 minutos (Desmarca lo que no esté disponible):**")
            cols_ed = st.columns(4)
            franjas_editadas_seleccionadas = []
            for idx_f, hora_f in enumerate(FRANJAS_HORARIAS_POSIBLES):
                default_chk = hora_f in franjas_guardadas_act if franjas_str_act else True
                with cols_ed[idx_f % 4]:
                    if st.checkbox(hora_f, value=default_chk, key=f"ed_f_{alumno_editar}_{hora_f}"):
                        franjas_editadas_seleccionadas.append(hora_f)
            
            if st.form_submit_button("Guardar Cambios"):
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Telefono"] = nuevo_tel_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Correo"] = nuevo_correo_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Circunstancias"] = nuevas_circ
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Asiste_Por_Defecto"] = nuevo_asiste_def
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Franja_Defecto"] = ",".join(franjas_editadas_seleccionadas)
                
                guardar_alumnos(df_alumnos_db)
                if alumno_editar != nuevo_nombre_val:
                    df_seguimiento.loc[df_seguimiento["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                    df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success("¡Perfil actualizado con éxito!")
                st.rerun()
                
    elif sub_opcion == "Añadir Nuevo Opositor":
        with st.form("form_nuevo_alumno"):
            n_nombre = st.text_input("Nombre y Apellidos")
            n_tel = st.text_input("Teléfono")
            n_correo = st.text_input("Correo")
            n_circ = st.text_area("Circunstancias")
            
            st.markdown("#### ⚙️ Preferencias Permanentes de Simulacro")
            n_asiste_def = st.checkbox("Asiste por defecto cada semana", value=True)
            
            st.markdown("**Disponibilidad por franjas de 15 minutos (Todas marcadas por defecto):**")
            cols_nue = st.columns(4)
            franjas_nuevas_seleccionadas = []
            for idx_f, hora_f in enumerate(FRANJAS_HORARIAS_POSIBLES):
                with cols_nue[idx_f % 4]:
                    if st.checkbox(hora_f, value=True, key=f"nue_f_{hora_f}"):
                        franjas_nuevas_seleccionadas.append(hora_f)
            
            if st.form_submit_button("Crear Opositor"):
                if n_nombre and n_nombre not in lista_alumnos:
                    nuevo_fila = pd.DataFrame({
                        "Alumno": [n_nombre], "Telefono": [n_tel], "Correo": [n_correo], "Circunstancias": [n_circ],
                        "Asiste_Por_Defecto": [n_asiste_def], "Franja_Defecto": [",".join(franjas_nuevas_seleccionadas)]
                    })
                    df_alumnos_db = pd.concat([df_alumnos_db, nuevo_fila], ignore_index=True)
                    guardar_alumnos(df_alumnos_db)
                    st.success("¡Opositor añadido con éxito!")
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
            st.info(f"📞 Teléfono: {p['Telefono']} | ✉️ Correo: {p['Correo']} | 📝 Circunstancias: {p['Circunstancias']} | ⏰ Disponibilidad Habitual: `{p['Franja_Defecto']}`")
        
        st.markdown("---")
        st.markdown("### 🧱 Detalle por Bloque de este Opositor")
        df_al_seg = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
        
        detalle_bloques = []
        total_temas_estudiados_alumno = 0
        total_faltas_injustificadas_alumno = 0
        
        for bloque in bloques_oposition:
            df_b = df_al_seg[df_al_seg["Bloque"] == bloque]
            temas_b = set()
            
            for _, r in df_b.iterrows():
                asis_r = str(r.get("Asistencia", "Asiste"))
                if asis_r == "Falta Injustificada":
                    total_faltas_injustificadas_alumno += 1
                else:
                    temas_b.update(parsear_temas(str(r["Temas_Para_Esta_Semana"])))
            
            lista_t = sorted(list(temas_b))
            num_t = len(temas_b)
            total_temas_estudiados_alumno += num_t
            
            detalle_bloques.append({
                "Bloque": bloque,
                "Total Temas Vistos": num_t,
                "Temas Concretos Estudiados": ", ".join(map(str, lista_t)) if lista_t else "Ninguno"
            })
            
        st.dataframe(pd.DataFrame(detalle_bloques), use_container_width=True)
        
        st.markdown("---")
        st.markdown("### ⏱️ Control de Desviación con el Calendario Teórico y Asistencia")
        TEMAS_TEORICOS_SEMANA_MEDIA = 5 
        semanas_registradas = max(len(df_al_seg), 1)
        temas_esperados_teoricos = semanas_registradas * TEMAS_TEORICOS_SEMANA_MEDIA
        
        diferencia_temas = temas_esperados_teoricos - total_temas_estudiados_alumno
        semanas_retraso = round(diferencia_temas / TEMAS_TEORICOS_SEMANA_MEDIA, 1)
        
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        col_d1.metric("Temas Acumulados Vistos", total_temas_estudiados_alumno)
        col_d2.metric("Faltas Injustificadas Totales", total_faltas_injustificadas_alumno)
        if semanas_retraso > 0:
            col_d3.metric("Desviación Estimada", f"+{semanas_retraso} sem. retraso", delta_color="inverse")
        else:
            col_d3.metric("Desviación Estimada", "Al día", delta_color="normal")
        col_d4.metric("Sesiones Registradas", len(df_al_seg))

        st.markdown("---")
        st.markdown("### 📋 Registro Histórico Detallado")
        if not df_al_seg.empty:
            st.dataframe(df_al_seg, use_container_width=True)
            csv_data = df_al_seg.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Histórico (CSV)", data=csv_data, file_name=f"historial_{alumno_filtro.replace(' ', '_')}.csv", mime="text/csv")
        else:
            st.info("Aún no hay registros guardados para este opositor.")
