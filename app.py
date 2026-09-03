elif menu == "📅 Control y Edición de Sesiones":
    st.subheader("📅 Control, Modificación y Eliminación de Sesiones Completas")
    if df_seguimiento.empty:
        st.info("No hay sesiones registradas.")
    else:
        # Agrupamos por fecha para tratar cada fecha como una sesión completa
        fechas_unicas = sorted(df_seguimiento["Fecha"].unique(), reverse=True)
        
        st.markdown("### Listado de Sesiones por Fecha")
        
        for fecha_sesion in fechas_unicas:
            df_sesion_actual = df_seguimiento[df_seguimiento["Fecha"] == fecha_sesion]
            bloques_en_sesion = df_sesion_actual["Bloque"].unique()
            bloques_str = ", ".join(bloques_en_sesion)
            num_alumnos_sesion = len(df_sesion_actual)
            
            with st.expander(f"📅 Fecha: {fecha_sesion} | 🧱 Bloques: {bloques_str} | 👥 Alumnos evaluados: {num_alumnos_sesion}"):
                
                # Botón para eliminar toda la sesión de esa fecha
                col_del1, col_del2 = st.columns([3, 1])
                with col_del2:
                    if st.button("🗑️ Eliminar Sesión Completa", key=f"btn_del_sesion_{fecha_sesion}"):
                        df_seguimiento = df_seguimiento[df_seguimiento["Fecha"] != fecha_sesion].reset_index(drop=True)
                        df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                        st.success(f"¡Sesión del día {fecha_sesion} eliminada por completo!")
                        st.rerun()
                
                st.markdown("---")
                st.markdown("#### 📝 Detalle de opositores en esta sesión")
                
                # Editor interactivo o formulario para actualizar los registros de esa fecha conjunta
                with st.form(f"form_edit_sesion_completa_{fecha_sesion}"):
                    # Permite cambiar la fecha de toda la sesión si fuera necesario
                    nueva_fecha_val = st.date_input(
                        "Fecha de la sesión", 
                        value=datetime.strptime(str(fecha_sesion), "%Y-%m-%d").date() if "-" in str(fecha_sesion) else datetime.today(), 
                        key=f"f_fecha_ses_{fecha_sesion}"
                    )
                    
                    registros_actualizados = []
                    for idx, row in df_sesion_actual.iterrows():
                        st.markdown(f"**Opositor: {row['Alumno']}** *(Bloque: {row['Bloque']})*")
                        c1, c2, c3 = st.columns(3)
                        
                        with c1:
                            asis_actual = str(row['Asistencia'])
                            idx_asis = opciones_asistencia.index(asis_actual) if asis_actual in opciones_asistencia else 0
                            nuevo_asis = st.selectbox(
                                "Asistencia", 
                                opciones_asistencia, 
                                index=idx_asis, 
                                key=f"asis_{fecha_sesion}_{idx}"
                            )
                        with c2:
                            nuevo_temas = st.text_input(
                                "Temas", 
                                value=str(row['Temas_Para_Esta_Semana']), 
                                key=f"temas_{fecha_sesion}_{idx}"
                            )
                        with c3:
                            nuevo_tema_esc = st.text_input(
                                "Tema Escrito", 
                                value=str(row['Tema_Escrito']), 
                                key=f"esc_{fecha_sesion}_{idx}"
                            )
                        
                        c4, c5 = st.columns(2)
                        with c4:
                            nuevo_tiempo = st.slider(
                                "Minutos", 
                                15, 90, 
                                int(row['Tiempo_Minutos']) if pd.notnull(row['Tiempo_Minutos']) and str(row['Tiempo_Minutos']).isdigit() else 60, 
                                key=f"tiempo_{fecha_sesion}_{idx}"
                            )
                        with c5:
                            sem_actual = str(row['Estado_Semaforo'])
                            opciones_sem = ["🟢 Consolidado / Vivo", "🟡 En estudio / Mejorable", "🔴 Bloqueado / Alerta"]
                            idx_sem = opciones_sem.index(sem_actual) if sem_actual in opciones_sem else 0
                            nuevo_sem = st.selectbox(
                                "Semáforo", 
                                opciones_sem, 
                                index=idx_sem, 
                                key=f"sem_{fecha_sesion}_{idx}"
                            )
                            
                        nuevo_feedback = st.text_area(
                            "Feedback Cualitativo", 
                            value=str(row['Feedback_Cualitativo']), 
                            key=f"feed_{fecha_sesion}_{idx}"
                        )
                        st.markdown("---")
                        
                        # Guardamos los datos modificados temporalmente para volcarlos al pulsar el botón global
                        registros_actualizados.append({
                            "index_original": idx,
                            "Fecha": str(nueva_fecha_val),
                            "Alumno": row['Alumno'],
                            "Bloque": row['Bloque'],
                            "Asistencia": nuevo_asis,
                            "Temas_Para_Esta_Semana": nuevo_temas,
                            "Tema_Escrito": nuevo_tema_esc,
                            "Tiempo_Minutos": nuevo_tiempo,
                            "Estado_Semaforo": nuevo_sem,
                            "Errores_Frecuentes": row['Errores_Frecuentes'],
                            "Feedback_Cualitativo": nuevo_feedback
                        })
                    
                    if st.form_submit_button("💾 Guardar Cambios de esta Sesión"):
                        for reg in registros_actualizados:
                            i_orig = reg["index_original"]
                            df_seguimiento.loc[i_orig, 'Fecha'] = reg["Fecha"]
                            df_seguimiento.loc[i_orig, 'Asistencia'] = reg["Asistencia"]
                            df_seguimiento.loc[i_orig, 'Temas_Para_Esta_Semana'] = reg["Temas_Para_Esta_Semana"]
                            df_seguimiento.loc[i_orig, 'Tema_Escrito'] = reg["Tema_Escrito"]
                            df_seguimiento.loc[i_orig, 'Tiempo_Minutos'] = reg["Tiempo_Minutos"]
                            df_seguimiento.loc[i_orig, 'Estado_Semaforo'] = reg["Estado_Semaforo"]
                            df_seguimiento.loc[i_orig, 'Feedback_Cualitativo'] = reg["Feedback_Cualitativo"]
                            
                        df_seguimiento.to_csv(DB_SEGUIMIENTO, index=False)
                        st.success("¡Sesión completa actualizada correctamente!")
                        st.rerun()
