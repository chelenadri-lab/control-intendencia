elif menu == "🕒 Turnos de Simulacro (En Vivo)":
    st.subheader("🕒 Gestión y Planificación de Turnos de Simulacro (Lunes Tarde)")
    fecha_simulacro = st.date_input("Fecha de la sesión de simulacros", datetime.today())
    
    st.markdown("---")
    st.markdown("### 🛠️ Paso 1: Configuración Rápida de Asistencia y Bloques")
    st.info("Modifica directamente en la tabla la asistencia y el bloque para esta sesión, y pulsa en guardar cambios.")

    df_config_tabla = df_alumnos_db[["Alumno", "Asiste_Por_Defecto", "Bloque_Habitual"]].copy()
    df_config_tabla.columns = ["Opositor", "Asiste (Sesión)", "Bloque de Materia"]

    df_editado = st.data_editor(
        df_config_tabla,
        column_config={
            "Opositor": st.column_config.TextColumn("Opositor", disabled=True),
            "Asiste (Sesión)": st.column_config.CheckboxColumn("Asiste (Sesión)", default=True),
            "Bloque de Materia": st.column_config.SelectboxColumn("Bloque de Materia", options=bloques_oposition, required=True)
        },
        hide_index=True,
        use_container_width=True,
        key="editor_config_sesion"
    )

    if st.button("💾 Guardar Configuración y Generar Registros Base"):
        for _, row_ed in df_editado.iterrows():
            al_nombre = row_ed["Opositor"]
            esta_asistiendo = row_ed["Asiste (Sesión)"]
            bl_asig = row_ed["Bloque de Materia"]
            
            estado_asis_str = "Asiste" if esta_asistiendo else "Falta Injustificada"
            
            df_alumnos_db.loc[df_alumnos_db["Alumno"] == al_nombre, "Asiste_Por_Defecto"] = esta_asistiendo
            df_alumnos_db.loc[df_alumnos_db["Alumno"] == al_nombre, "Bloque_Habitual"] = bl_asig
            
            nuevo_reg = pd.DataFrame({
                "Fecha": [str(fecha_simulacro)], "Alumno": [al_nombre], "Bloque": [bl_asig],
                "Asistencia": [estado_asis_str], "Temas_Para_Esta_Semana": [""], 
                "Tema_Escrito": [""], "Tiempo_Minutos": [0], 
                "Estado_Semaforo": ["🟢 Consolidado / Vivo"], "Errores_Frecuentes": [""], 
                "Feedback_Cualitativo": ["Generado automáticamente desde planificación rápida."]
            })
            df_seguimiento = pd.concat([df_seguimiento, nuevo_reg], ignore_index=True)
            
        guardar_alumnos(df_alumnos_db)
        df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
        st.toast("¡Configuración guardada y parrilla inicial generada!", icon="✅")

    st.markdown("---")
    st.markdown("### ⏰ Paso 2: Parrilla de Entradas (Respetando Disponibilidad Horaria)")
    
    alumnos_asistentes = df_editado[df_editado["Asiste (Sesión)"] == True]["Opositor"].tolist()
    
    if not alumnos_asistentes:
        st.warning("No hay alumnos marcados como asistentes en la tabla superior.")
    else:
        # Generamos la lista de horas estándar cada 15 min desde las 16:00
        hora_inicio = datetime.strptime("16:00", "%H:%M")
        franjas_horarias = []
        for i in range(len(alumnos_asistentes)):
            franjas_horarias.append((hora_inicio + timedelta(minutes=15 * i)).strftime("%H:%M"))
        
        # Asignación inteligente respetando preferencias individuales de franja
        alumnos_ordenados_por_preferencia = []
        alumnos_restantes = list(alumnos_asistentes)
        
        # Primero colocamos a los que tengan preferencia por las horas más tempranas según su perfil
        for hora in franjas_horarias:
            asignado_en_hora = False
            for al in list(alumnos_restantes):
                row_perfil = df_alumnos_db[df_alumnos_db["Alumno"] == al]
                if not row_perfil.empty:
                    franjas_disp_str = str(row_perfil.iloc[0]["Franja_Defecto"])
                    # Si el alumno tiene esta hora concreta dentro de sus preferencias guardadas
                    if hora in franjas_disp_str:
                        alumnos_ordenados_por_preferencia.append(al)
                        alumnos_restantes.remove(al)
                        asignado_en_hora = True
                        break
            # Si nadie específico reclamaba exactamente esta hora, rellenamos con el primero que quede libre
            if not asignado_en_hora and alumnos_restantes:
                al = alumnos_restantes.pop(0)
                alumnos_ordenados_por_preferencia.append(al)

        with st.form("form_ver_parrilla"):
            for idx, hora in enumerate(franjas_horarias):
                col_h, col_a, col_t = st.columns([1, 2, 1])
                with col_h:
                    st.markdown(f"### ⏰ {hora}")
                with col_a:
                    def_al = alumnos_ordenados_por_preferencia[idx]
                    st.selectbox(f"Opositor a las {hora}", alumnos_asistentes, index=alumnos_asistentes.index(def_al), key=f"parrilla_al_{idx}")
                with col_t:
                    st.markdown(f"**Prueba:** `Lectura Tema Escrito`")
                
            if st.form_submit_button("💾 Guardar Parrilla Definitiva"):
                st.success("¡Parrilla de la tarde fijada correctamente respetando disponibilidades!")

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
            errores_flash = st.multiselect("Etiquetas de Errores", OPCIONES_ERRORES, key="f_err")
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
