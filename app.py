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
        if "Asiste_Por_Defecto" not in df.columns:
            df["Asiste_Por_Defecto"] = True
        if "Tipo_Prueba_Defecto" not in df.columns:
            df["Tipo_Prueba_Defecto"] = "Simulacro Oral"
        if "Franja_Defecto" not in df.columns:
            df["Franja_Defecto"] = "Sin preferencia (Cualquier hora)"
            
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
            "Tipo_Prueba_Defecto": ["Simulacro Oral" for _ in ALUMNOS_INICIALES],
            "Franja_Defecto": ["Sin preferencia (Cualquier hora)" for _ in ALUMNOS_INICIALES]
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
    "📝 Registrar Sesión / Ficha (General)", 
    "📊 Cuadro Resumen y Progreso", 
    "👥 Gestión de Opositores y Perfiles",
    "📊 Histórico, Bloques y Desviación"
])

if menu == "🕒 Turnos de Simulacro (En Vivo)":
    st.subheader("🕒 Gestión y Planificación de Turnos de Simulacro (Lunes Tarde)")
    fecha_simulacro = st.date_input("Fecha de la sesión de simulacros", datetime.today())
    
    st.markdown("---")
    st.markdown("### 🛠️ Paso 1: Configuración Previa de la Sesión")
    st.info("Los valores se cargan automáticamente según las preferencias permanentes de cada alumno. Puedes ajustarlos puntualmente para esta sesión si hay cambios y opcionalmente actualizar su perfil fijo.")
    
    opciones_franja = [
        "Sin preferencia (Cualquier hora)", 
        "Solo de 16:00 a 18:00 (Tarde temprana)", 
        "A partir de las 18:00 (Tarde tardía)",
        "Primer turno absoluto (16:00)"
    ]
    opciones_tipo = ["Simulacro Oral", "Test"]

    with st.form("form_configuracion_sesion"):
        configuracion_alumnos = {}
        
        for alumno in lista_alumnos:
            row_al = df_alumnos_db[df_alumnos_db["Alumno"] == alumno].iloc[0]
            def_asiste = bool(row_al["Asiste_Por_Defecto"])
            def_tipo = row_al["Tipo_Prueba_Defecto"] if row_al["Tipo_Prueba_Defecto"] in opciones_tipo else "Simulacro Oral"
            def_franja = row_al["Franja_Defecto"] if row_al["Franja_Defecto"] in opciones_franja else opciones_franja[0]
            
            with st.expander(f"👤 {alumno}"):
                col_c1, col_c2, col_c3 = st.columns([1, 1, 2])
                with col_c1:
                    asiste = st.checkbox("Asiste esta semana", value=def_asiste, key=f"asiste_{alumno}")
                with col_c2:
                    tipo_prueba = st.selectbox("Tipo de prueba", opciones_tipo, index=opciones_tipo.index(def_tipo), key=f"tipo_{alumno}")
                with col_c3:
                    franja = st.selectbox("Franja horaria habitual / preferida", opciones_franja, index=opciones_franja.index(def_franja), key=f"franja_{alumno}")
                
                configuracion_alumnos[alumno] = {
                    "asiste": asiste,
                    "tipo": tipo_prueba,
                    "franja": franja
                }
        
        actualizar_permanentes = st.checkbox("💾 Actualizar también las preferencias permanentes en los perfiles de los alumnos con estos cambios", value=False)
        btn_generar_parrilla = st.form_submit_button("⚙️ Generar y Bloquear Parrilla de Turnos Automática")

        if btn_generar_parrilla and actualizar_permanentes:
            for al, cfg in configuracion_alumnos.items():
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == al, "Asiste_Por_Defecto"] = cfg["asiste"]
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == al, "Tipo_Prueba_Defecto"] = cfg["tipo"]
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == al, "Franja_Defecto"] = cfg["franja"]
            guardar_alumnos(df_alumnos_db)
            st.toast("¡Preferencias permanentes actualizadas en los perfiles!", icon="✅")

    st.markdown("---")
    st.markdown("### ⏰ Paso 2: Parrilla de Entradas (Cada 15 min desde las 16:00)")
    
    alumnos_asistentes = [al for al, cfg in configuracion_alumnos.items() if cfg["asiste"]]
    
    if not alumnos_asistentes:
        st.warning("No hay alumnos marcados como asistentes para esta sesión.")
    else:
        hora_inicio = datetime.strptime("16:00", "%H:%M")
        franjas_horarias = []
        for i in range(len(alumnos_asistentes)):
            franjas_horarias.append((hora_inicio + timedelta(minutes=15 * i)).strftime("%H:%M"))
        
        def regla_orden(nombre):
            franja_val = configuracion_alumnos[nombre]["franja"]
            if "Primer turno" in franja_val: return 0
            elif "16:00 a 18:00" in franja_val: return 1
            elif "Sin preferencia" in franja_val: return 2
            else: return 3
            
        alumnos_ordenados = sorted(alumnos_asistentes, key=regla_orden)
        
        with st.form("form_ver_parrilla"):
            horarios_fijados = {}
            for idx, hora in enumerate(franjas_horarias):
                col_h, col_a, col_t = st.columns([1, 2, 1])
                with col_h:
                    st.markdown(f"### ⏰ {hora}")
                with col_a:
                    def_al = alumnos_ordenados[idx] if idx < len(alumnos_ordenados) else alumnos_asistentes[0]
                    al_asignado = st.selectbox(f"Opositor a las {hora}", alumnos_asistentes, index=alumnos_asistentes.index(def_al), key=f"parrilla_al_{idx}")
                with col_t:
                    tipo_p = configuracion_alumnos[al_asignado]["tipo"]
                    st.markdown(f"**Tipo:** `{tipo_p}`")
                horarios_fijados[hora] = al_asignado
                
            if st.form_submit_button("💾 Guardar Parrilla Definitiva"):
                st.success("¡Parrilla de la tarde fijada correctamente!")

    st.markdown("---")
    st.markdown("### ⚡ Paso 3: Evaluación Rápida en Consulta (Entrada por la Puerta)")
    
    if lista_alumnos:
        alumno_en_puerta = st.selectbox("Opositor que entra a consulta ahora mismo:", lista_alumnos, key="puerta_select")
        perfil_puerta = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_en_puerta]
        if not perfil_puerta.empty and perfil_puerta.iloc[0]["Circunstancias"] and perfil_puerta.iloc[0]["Circunstancias"] != "nan":
            st.warning(f"📝 **Circunstancias:** {perfil_puerta.iloc[0]['Circunstancias']}")

        with st.form("form_evaluacion_flash"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                bloque_flash = st.selectbox("Bloque de Materia", bloques_oposition, key="f_bloque")
                asistencia_flash = st.selectbox(
                    "Control de Asistencia", 
                    ["Asiste", "Justificado (Estudio / Test)", "Falta Injustificada"], 
                    key="f_asis"
                )
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

elif menu == "📝 Registrar Sesión / Ficha (General)":
    st.subheader("📝 Ficha General de Seguimiento")
    if lista_alumnos:
        with st.form("form_general"):
            al_gen = st.selectbox("Opositor", lista_alumnos, key="g_al")
            bl_gen = st.selectbox("Bloque", bloques_oposition, key="g_bl")
            asis_gen = st.selectbox("Asistencia", ["Asiste", "Justificado (Estudio / Test)", "Falta Injustificada"], key="g_asis")
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
                    "Asistencia": [asis_gen], "Temas_Para_Esta_Semana": [t_sem_gen], 
                    "Tema_Escrito": [t_esc_gen], "Tiempo_Minutos": [t_min_gen], 
                    "Estado_Semaforo": [sem_gen], "Errores_Frecuentes": [", ".join(err_gen)], 
                    "Feedback_Cualitativo": [feed_gen]
                })
                df_seguimiento = pd.concat([df_seguimiento, reg_gen], ignore_index=True)
                df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                st.success("Guardado correctamente.")

elif menu == "📊 Cuadro Resumen y Progreso":
    st.subheader("📊 Cuadro Resumen Global por Opositor y Bloques")
    if df_seguimiento.empty:
        st.info("Todavía no hay registros guardados.")
    else:
        st.markdown("### 📋 Matriz General de Avance (Temas Vistos y Faltas Injustificadas)")
        matriz_data = []
        for alumno in lista_alumnos:
            fila = {"Opositor": alumno}
            df_al = df_seguimiento[df_seguimiento["Alumno"] == alumno]
            
            for bloque in bloques_oposition:
                df_bloque = df_al[df_al["Bloque"] == bloque]
                temas_totales_set = set()
                faltas_injustificadas_bloque = 0
                
                for _, row in df_bloque.iterrows():
                    asis = str(row.get("Asistencia", "Asiste"))
                    if asis == "Falta Injustificada":
                        faltas_injustificadas_bloque += 1
                    elif asis == "Asiste":
                        temas_totales_set.update(parsear_temas(str(row["Temas_Para_Esta_Semana"])))
                    elif "Justificado" in asis:
                        # Si está justificado por estudio/test, también puede sumar temas si los preparó
                        temas_totales_set.update(parsear_temas(str(row["Temas_Para_Esta_Semana"])))
                
                lista_ordenada = sorted(list(temas_totales_set))
                
                detalle_str = f"({len(temas_totales_set)} temas)"
                if lista_ordenada:
                    detalle_str += f" [{', '.join(map(str, lista_ordenada))}]"
                
                if faltas_injustificadas_bloque > 0:
                    detalle_str += f" ❌ [Faltas inj.: {faltas_injustificadas_bloque}]"
                else:
                    detalle_str += " ✅ [0 faltas inj.]"
                    
                fila[bloque] = detalle_str
            matriz_data.append(fila)
        
        st.dataframe(pd.DataFrame(matriz_data), use_container_width=True)

elif menu == "👥 Gestión de Opositores y Perfiles":
    st.subheader("👥 Gestión de Alumnos y Perfiles")
    if not lista_alumnos:
        sub_opcion = "Añadir Nuevo Opositor"
    else:
        sub_opcion = st.radio("¿Qué deseas hacer?", ["Editar Perfil Existente", "Añadir Nuevo Opositor", "Eliminar Opositor"])
    
    opciones_franja = [
        "Sin preferencia (Cualquier hora)", 
        "Solo de 16:00 a 18:00 (Tarde temprana)", 
        "A partir de las 18:00 (Tarde tardía)",
        "Primer turno absoluto (16:00)"
    ]
    opciones_tipo = ["Simulacro Oral", "Test"]

    if sub_opcion == "Editar Perfil Existente" and lista_alumnos:
        alumno_editar = st.selectbox("Selecciona opositor", lista_alumnos)
        datos_actuales = df_alumnos_db[df_alumnos_db["Alumno"] == alumno_editar].iloc[0]
        
        with st.form("form_editar_alumno"):
            nuevo_nombre_val = st.text_input("Nombre y Apellidos", value=str(datos_actuales["Alumno"]))
            nuevo_tel_val = st.text_input("Teléfono", value=str(datos_actuales["Telefono"]))
            nuevo_correo_val = st.text_input("Correo", value=str(datos_actuales["Correo"]))
            nuevas_circ = st.text_area("Circunstancias", value=str(datos_actuales["Circunstancias"]))
            
            st.markdown("#### ⚙️ Preferencias Permanentes de Simulacro")
            val_asiste_def = bool(datos_actuales["Asiste_Por_Defecto"])
            val_tipo_def = datos_actuales["Tipo_Prueba_Defecto"] if datos_actuales["Tipo_Prueba_Defecto"] in opciones_tipo else "Simulacro Oral"
            val_franja_def = datos_actuales["Franja_Defecto"] if datos_actuales["Franja_Defecto"] in opciones_franja else opciones_franja[0]
            
            nuevo_asiste_def = st.checkbox("Asiste por defecto cada semana", value=val_asiste_def)
            nuevo_tipo_def = st.selectbox("Tipo de prueba habitual", opciones_tipo, index=opciones_tipo.index(val_tipo_def))
            nueva_franja_def = st.selectbox("Franja horaria preferida por defecto", opciones_franja, index=opciones_franja.index(val_franja_def))
            
            if st.form_submit_button("Guardar Cambios"):
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == alumno_editar, "Alumno"] = nuevo_nombre_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Telefono"] = nuevo_tel_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Correo"] = nuevo_correo_val
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Circunstancias"] = nuevas_circ
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Asiste_Por_Defecto"] = nuevo_asiste_def
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Tipo_Prueba_Defecto"] = nuevo_tipo_def
                df_alumnos_db.loc[df_alumnos_db["Alumno"] == nuevo_nombre_val, "Franja_Defecto"] = nueva_franja_def
                
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
            n_tipo_def = st.selectbox("Tipo de prueba habitual", opciones_tipo)
            n_franja_def = st.selectbox("Franja horaria preferida por defecto", opciones_franja)
            
            if st.form_submit_button("Crear Opositor"):
                if n_nombre and n_nombre not in lista_alumnos:
                    nuevo_fila = pd.DataFrame({
                        "Alumno": [n_nombre], "Telefono": [n_tel], "Correo": [n_correo], "Circunstancias": [n_circ],
                        "Asiste_Por_Defecto": [n_asiste_def], "Tipo_Prueba_Defecto": [n_tipo_def], "Franja_Defecto": [n_franja_def]
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
            st.info(f"📞 Teléfono: {p['Telefono']} | ✉️ Correo: {p['Correo']} | 📝 Circunstancias: {p['Circunstancias']} | ⏰ Franja Habitual: `{p['Franja_Defecto']}`")
        
        st.markdown("---")
        st.markdown("### 🧱 Detalle por Bloque de este Opositor")
        df_al_seg = df_seguimiento[df_seguimiento["Alumno"] == alumno_filtro]
        
        detalle_bloques = []
        total_temas_estudiados_alumno = 0
        total_faltas_injustificadas_alumno = 0
        
        for bloque in bloques_oposition:
            df_b = df_al_seg[df_al_seg["Bloque"] == bloque]
            temas_b = set()
            faltas_inj_b = 0
            
            for _, r in df_b.iterrows():
                asis_r = str(r.get("Asistencia", "Asiste"))
                if asis_r == "Falta Injustificada":
                    faltas_inj_b += 1
                elif asis_r == "Asiste":
                    temas_b.update(parsear_temas(str(r["Temas_Para_Esta_Semana"])))
                elif "Justificado" in asis_r:
                    temas_b.update(parsear_temas(str(r["Temas_Para_Esta_Semana"])))
            
            lista_t = sorted(list(temas_b))
            num_t = len(temas_b)
            total_temas_estudiados_alumno += num_t
            total_faltas_injustificadas_alumno += faltas_inj_b
            
            detalle_bloques.append({
                "Bloque": bloque,
                "Total Temas Vistos": num_t,
                "Faltas Injustificadas": faltas_inj_b,
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
