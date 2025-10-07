import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar componentes
sys.path.append(str(Path(__file__).parent.parent))

from components.data_loader import DataLoader
from components.validators import DataValidator
from components.model_runner import ModelRunner

st.set_page_config(
    page_title="Configuración - Modelo Cajas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Configuración de Parámetros")
st.markdown("Carga y edita los parámetros del modelo de optimización")

# Tabs para diferentes opciones de carga
tab1, tab2, tab3 = st.tabs(["📁 Cargar Archivos", "📝 Editar Datos", "✅ Validar"])

# ==================== TAB 1: CARGAR ARCHIVOS ====================
with tab1:
    st.header("Cargar Parámetros")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### Opciones de Carga:
        1. **Desde CSVs existentes**: Usa los archivos que ya están en `inputs/csv/`
        2. **Subir nuevos archivos**: Sube un Excel o múltiples CSVs
        """)

    with col2:
        st.info("""
        **Archivos necesarios:**
        - Turnos
        - Disponibilidad Máquinas
        - Productividad Máquina-Caja
        - Tiempo de Setup
        - Duración Turno
        """)

    st.markdown("---")

    # Opción 1: Usar archivos existentes
    if st.button("📂 Cargar desde inputs/csv/", type="primary", use_container_width=True):
        with st.spinner("Cargando datos..."):
            csv_path = Path(__file__).parent.parent / "inputs" / "csv"

            if csv_path.exists():
                dataframes = DataLoader.load_from_csv_folder(str(csv_path))

                if dataframes:
                    # Validar
                    is_valid, errors = DataLoader.validate_all_data(dataframes)

                    if is_valid:
                        st.session_state.dataframes = dataframes
                        st.session_state.datos_cargados = True

                        # Inicializar modelo
                        runner = ModelRunner()
                        if runner.initialize_from_dataframes(dataframes):
                            params = runner.extract_parameters()
                            if params:
                                st.session_state.parametros = params
                                st.session_state.modelo_cargado = True
                                st.success("✅ Datos cargados y validados correctamente")
                                st.rerun()
                    else:
                        st.error("❌ Errores en la validación:")
                        for error in errors:
                            st.error(f"- {error}")
                else:
                    st.error("No se pudieron cargar los archivos CSV")
            else:
                st.error(f"No existe la carpeta: {csv_path}")

    st.markdown("---")

    # Descargar templates
    st.subheader("📥 Descargar Templates")
    st.info("Descarga los archivos de ejemplo para entender el formato requerido")

    col1, col2, col3, col4, col5 = st.columns(5)

    template_path = Path(__file__).parent.parent / "templates"

    with col1:
        template_file = template_path / "Turnos.csv"
        if template_file.exists():
            with open(template_file, 'rb') as f:
                st.download_button(
                    "📄 Turnos.csv",
                    data=f.read(),
                    file_name="Turnos_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with col2:
        template_file = template_path / "Disponibilidad_Maquinas.csv"
        if template_file.exists():
            with open(template_file, 'rb') as f:
                st.download_button(
                    "📄 Disponibilidad",
                    data=f.read(),
                    file_name="Disponibilidad_Maquinas_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with col3:
        template_file = template_path / "Productividad_Maquina_Caja.csv"
        if template_file.exists():
            with open(template_file, 'rb') as f:
                st.download_button(
                    "📄 Productividad",
                    data=f.read(),
                    file_name="Productividad_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with col4:
        template_file = template_path / "Tiempo_de_Setup_por_maquina.csv"
        if template_file.exists():
            with open(template_file, 'rb') as f:
                st.download_button(
                    "📄 Setup",
                    data=f.read(),
                    file_name="Setup_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with col5:
        template_file = template_path / "Duracion_Turno.csv"
        if template_file.exists():
            with open(template_file, 'rb') as f:
                st.download_button(
                    "📄 Duración Turno",
                    data=f.read(),
                    file_name="Duracion_Turno_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    st.markdown("---")

    # Opción 2: Subir archivos
    st.subheader("O sube nuevos archivos:")

    dataframes_uploaded = DataLoader.upload_files_widget(key="main_upload")

    if dataframes_uploaded:
        # Validar formato de archivos primero
        st.subheader("🔍 Validando formato de archivos...")

        format_errors = {}
        for file_type, df in dataframes_uploaded.items():
            is_format_valid, format_msgs = DataValidator.validate_file_format(df, file_type)
            if not is_format_valid:
                format_errors[file_type] = format_msgs

        if format_errors:
            st.error("❌ Errores de formato detectados:")
            for file_type, msgs in format_errors.items():
                st.error(f"**{file_type}:**")
                for msg in msgs:
                    st.write(f"  - {msg}")
            st.warning("💡 Descarga los templates para ver el formato correcto")
        else:
            st.success("✅ Formato de archivos correcto")

            # Validar datos
            is_valid, errors = DataLoader.validate_all_data(dataframes_uploaded)

            if is_valid:
                st.success("✅ Datos validados correctamente")

                if st.button("💾 Usar estos datos", type="primary"):
                    st.session_state.dataframes = dataframes_uploaded
                    st.session_state.datos_cargados = True

                    # Inicializar modelo
                    runner = ModelRunner()
                    if runner.initialize_from_dataframes(dataframes_uploaded):
                        params = runner.extract_parameters()
                        if params:
                            st.session_state.parametros = params
                            st.session_state.modelo_cargado = True
                            st.success("✅ Datos guardados en sesión")
                            st.rerun()
            else:
                st.error("❌ Errores en la validación de datos:")
                for error in errors:
                    st.error(f"- {error}")

# ==================== TAB 2: EDITAR DATOS ====================
with tab2:
    st.header("Editar Datos Cargados")

    if not st.session_state.datos_cargados:
        st.warning("⚠️ Primero carga datos en la pestaña 'Cargar Archivos'")
    else:
        dataframes = st.session_state.dataframes

        # Selector de tabla a editar
        tabla_seleccionada = st.selectbox(
            "Selecciona tabla para editar:",
            list(dataframes.keys())
        )

        st.markdown(f"### Editando: {tabla_seleccionada}")

        # Editor de datos
        df_editado = st.data_editor(
            dataframes[tabla_seleccionada],
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{tabla_seleccionada}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Guardar Cambios", type="primary"):
                st.session_state.dataframes[tabla_seleccionada] = df_editado

                # Re-inicializar modelo con datos actualizados
                runner = ModelRunner()
                if runner.initialize_from_dataframes(st.session_state.dataframes):
                    params = runner.extract_parameters()
                    if params:
                        st.session_state.parametros = params
                        st.success("✅ Cambios guardados correctamente")
                        st.rerun()

        with col2:
            if st.button("🔄 Descartar Cambios"):
                st.rerun()

# ==================== TAB 3: VALIDAR ====================
with tab3:
    st.header("Validación de Datos")

    if not st.session_state.datos_cargados:
        st.warning("⚠️ Primero carga datos en la pestaña 'Cargar Archivos'")
    else:
        dataframes = st.session_state.dataframes

        st.subheader("🔍 Resumen de Datos")

        # Resumen general
        summary = DataLoader.get_data_summary(dataframes)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total de Tablas", summary['total_sheets'])

        with col2:
            total_rows = sum(s['rows'] for s in summary['sheets'].values())
            st.metric("Total de Registros", total_rows)

        st.markdown("---")

        # Detalle por tabla
        for name, info in summary['sheets'].items():
            with st.expander(f"📋 {name} ({info['rows']} filas, {info['columns']} columnas)"):
                st.write("**Columnas:**", ", ".join(info['column_names']))

        st.markdown("---")

        # Validación detallada
        if st.button("🔍 Ejecutar Validación Completa", type="primary"):
            with st.spinner("Validando..."):
                is_valid, all_errors = DataValidator.validate_all(dataframes)

                if is_valid:
                    st.success("✅ Todos los datos son válidos")
                else:
                    st.error("❌ Se encontraron errores:")
                    for tabla, errores in all_errors.items():
                        st.error(f"**{tabla}:**")
                        for error in errores:
                            st.write(f"  - {error}")

                # Verificar consistencia
                warnings = DataValidator.check_consistency(dataframes)

                if warnings:
                    st.warning("⚠️ Advertencias de consistencia:")
                    for warning in warnings:
                        st.warning(f"- {warning}")
                else:
                    st.success("✅ Los datos son consistentes entre tablas")

# ==================== SIDEBAR INFO ====================
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Datos Cargados")

    if st.session_state.datos_cargados:
        st.success("✅ Datos disponibles")

        if st.session_state.parametros:
            params = st.session_state.parametros

            st.metric("Máquinas", len(params.get('M', [])))
            st.metric("Días", len(params.get('D', [])))
            st.metric("Tipos de Caja", len(params.get('B', [])))

            with st.expander("Ver Detalles"):
                st.write("**Máquinas:**", params.get('M', []))
                st.write("**Días:**", params.get('D', []))
                st.write("**Tipos de Caja:**", params.get('B', []))
    else:
        st.info("No hay datos cargados")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💡 Los cambios se guardan automáticamente en la sesión actual</p>
</div>
""", unsafe_allow_html=True)
