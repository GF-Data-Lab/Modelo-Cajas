"""Página para cargar y validar archivos de entrada."""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from styles.common_styles import configure_page
from utils import show_logo

# Configurar página
configure_page("Cargar Archivos", "📤", "wide")

# Sidebar
with st.sidebar:
    show_logo()
    st.markdown("---")
    st.markdown("### 📤 Cargar Datos")
    st.info("Sube los archivos Excel con los parámetros y la demanda")

st.title("📤 Cargar Archivos de Entrada")

st.markdown("""
### Archivos Requeridos

Para ejecutar el modelo de optimización necesitas cargar dos archivos Excel:

1. **Parametros.xlsx**: Contiene la configuración de las plantas, máquinas, turnos, etc.
2. **Libro7.xlsx**: Contiene la demanda de cajas a producir

Los archivos serán validados automáticamente antes de ser guardados.
""")

st.markdown("---")

# =============================================================================
# FUNCIONES DE VALIDACIÓN
# =============================================================================

def validar_parametros(df_dict):
    """
    Valida que el archivo Parametros.xlsx tenga la estructura correcta.

    Returns:
        tuple: (bool, list) - (es_valido, lista_errores)
    """
    errores = []
    hojas_requeridas = {
        'Planta': ['PLANTA'],
        'Turnos': ['PLANTA', 'DIA', 'CANTIDAD DE TURNOS'],
        'Disponibilidad Maquinas': ['PLANTA', 'DIA', 'MAQUINA', 'DISPONIBILIDAD'],
        'Productividad Máquina_Caja': ['PLANTA', 'MAQUINA', 'TIPO_CAJA', 'PRODUCTIVIDAD_CAJAS_HORA'],
        'Tiempo de Setup por máquina': ['PLANTA', 'MAQUINA', 'TIPO_CAJA_ACTUAL', 'TIPO_CAJA_A_CAMBIAR', 'HORA_SETUP'],
        'Duracion Turno': ['PLANTA', 'DIA', 'TURNO', 'HORAS']
    }

    # Verificar que existan todas las hojas
    for hoja in hojas_requeridas.keys():
        if hoja not in df_dict:
            errores.append(f"❌ Falta la hoja '{hoja}'")

    # Verificar columnas en cada hoja
    for hoja, columnas in hojas_requeridas.items():
        if hoja in df_dict:
            df = df_dict[hoja]
            for col in columnas:
                if col not in df.columns:
                    errores.append(f"❌ La hoja '{hoja}' no tiene la columna '{col}'")

            # Verificar que no esté vacía
            if len(df) == 0:
                errores.append(f"⚠️ La hoja '{hoja}' está vacía")

    return len(errores) == 0, errores


def validar_demanda(df):
    """
    Valida que el archivo Libro7.xlsx (demanda) tenga la estructura correcta.

    Returns:
        tuple: (bool, list) - (es_valido, lista_errores)
    """
    errores = []

    columnas_requeridas = [
        'DES_PLANTA', 'DESC_ESPECIE', 'DESC_VARIEDAD',
        'DESC_ENVASE', 'cajas_asignadas', 'fecha_planificación'
    ]

    # Verificar columnas
    for col in columnas_requeridas:
        if col not in df.columns:
            errores.append(f"❌ Falta la columna '{col}'")

    # Verificar que no esté vacío
    if len(df) == 0:
        errores.append(f"❌ El archivo de demanda está vacío")

    # Verificar tipos de datos básicos
    if 'cajas_asignadas' in df.columns:
        try:
            pd.to_numeric(df['cajas_asignadas'], errors='coerce')
        except:
            errores.append(f"⚠️ La columna 'cajas_asignadas' debe contener números")

    return len(errores) == 0, errores


# =============================================================================
# CARGA DE ARCHIVO DE PARAMETROS
# =============================================================================

st.subheader("1️⃣ Archivo de Parámetros")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_parametros = st.file_uploader(
        "Selecciona el archivo Parametros.xlsx",
        type=['xlsx', 'xls'],
        key='parametros_upload',
        help="Archivo Excel con las hojas: Planta, Turnos, Disponibilidad Maquinas, etc."
    )

with col2:
    st.markdown("**Estado:**")
    if 'parametros_validado' in st.session_state and st.session_state.parametros_validado:
        st.success("✅ Validado")
    else:
        st.info("⏳ Pendiente")

if uploaded_parametros is not None:
    try:
        # Leer todas las hojas
        excel_file = pd.ExcelFile(uploaded_parametros)
        df_dict = {sheet: excel_file.parse(sheet) for sheet in excel_file.sheet_names}

        st.success(f"✅ Archivo cargado: {uploaded_parametros.name}")

        # Mostrar información básica
        with st.expander("📋 Información del archivo", expanded=False):
            st.write(f"**Hojas encontradas:** {len(df_dict)}")
            for hoja, df in df_dict.items():
                st.write(f"- **{hoja}**: {len(df)} filas, {len(df.columns)} columnas")

        # Validar
        es_valido, errores = validar_parametros(df_dict)

        if es_valido:
            st.success("✅ Archivo validado correctamente")

            # Guardar en session state
            st.session_state['parametros_dict'] = df_dict
            st.session_state['parametros_validado'] = True
            st.session_state['parametros_nombre'] = uploaded_parametros.name

            # Guardar archivo físicamente
            output_path = Path("inputs/Parametros.xlsx")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Guardar el archivo subido
            with open(output_path, 'wb') as f:
                f.write(uploaded_parametros.getvalue())

            st.info(f"💾 Archivo guardado en: {output_path}")

            # Mostrar resumen
            with st.expander("📊 Resumen de Plantas", expanded=True):
                if 'Planta' in df_dict:
                    plantas = df_dict['Planta']['PLANTA'].tolist()
                    st.write(f"**Plantas disponibles:** {', '.join(plantas)}")

                    # Mostrar info por planta
                    for planta in plantas:
                        st.markdown(f"**{planta}:**")

                        # Máquinas
                        if 'Disponibilidad Maquinas' in df_dict:
                            maquinas = df_dict['Disponibilidad Maquinas'][
                                df_dict['Disponibilidad Maquinas']['PLANTA'] == planta
                            ]['MAQUINA'].nunique()
                            st.write(f"  - Máquinas: {maquinas}")

                        # Tipos de caja
                        if 'Productividad Máquina_Caja' in df_dict:
                            tipos_caja = df_dict['Productividad Máquina_Caja'][
                                df_dict['Productividad Máquina_Caja']['PLANTA'] == planta
                            ]['TIPO_CAJA'].nunique()
                            st.write(f"  - Tipos de caja: {tipos_caja}")
        else:
            st.error("❌ El archivo tiene errores de validación:")
            for error in errores:
                st.write(error)
            st.session_state['parametros_validado'] = False

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {str(e)}")
        st.session_state['parametros_validado'] = False

st.markdown("---")

# =============================================================================
# CARGA DE ARCHIVO DE DEMANDA
# =============================================================================

st.subheader("2️⃣ Archivo de Demanda")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_demanda = st.file_uploader(
        "Selecciona el archivo Libro7.xlsx (Demanda)",
        type=['xlsx', 'xls'],
        key='demanda_upload',
        help="Archivo Excel con la demanda de cajas a producir"
    )

with col2:
    st.markdown("**Estado:**")
    if 'demanda_validado' in st.session_state and st.session_state.demanda_validado:
        st.success("✅ Validado")
    else:
        st.info("⏳ Pendiente")

if uploaded_demanda is not None:
    try:
        # Leer archivo
        df_demanda = pd.read_excel(uploaded_demanda)

        st.success(f"✅ Archivo cargado: {uploaded_demanda.name}")

        # Mostrar información básica
        with st.expander("📋 Información del archivo", expanded=False):
            st.write(f"**Registros:** {len(df_demanda)}")
            st.write(f"**Columnas:** {len(df_demanda.columns)}")
            st.write("**Primeras 5 filas:**")
            st.dataframe(df_demanda.head(), use_container_width=True)

        # Validar
        es_valido, errores = validar_demanda(df_demanda)

        if es_valido:
            st.success("✅ Archivo validado correctamente")

            # Guardar en session state
            st.session_state['demanda_df'] = df_demanda
            st.session_state['demanda_validado'] = True
            st.session_state['demanda_nombre'] = uploaded_demanda.name

            # Guardar archivo físicamente
            output_path = Path("inputs/Libro7.xlsx")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(uploaded_demanda.getvalue())

            st.info(f"💾 Archivo guardado en: {output_path}")

            # Mostrar resumen
            with st.expander("📊 Resumen de Demanda", expanded=True):
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    if 'DES_PLANTA' in df_demanda.columns:
                        plantas = df_demanda['DES_PLANTA'].nunique()
                        st.metric("Plantas", plantas)
                        st.write("**Plantas:**")
                        for planta in df_demanda['DES_PLANTA'].unique():
                            registros = len(df_demanda[df_demanda['DES_PLANTA'] == planta])
                            st.write(f"- {planta}: {registros} registros")

                with col_b:
                    if 'cajas_asignadas' in df_demanda.columns:
                        total_cajas = df_demanda['cajas_asignadas'].sum()
                        st.metric("Total Cajas", f"{total_cajas:,.0f}")

                with col_c:
                    if 'DESC_ENVASE' in df_demanda.columns:
                        tipos_envase = df_demanda['DESC_ENVASE'].nunique()
                        st.metric("Tipos de Envase", tipos_envase)
        else:
            st.error("❌ El archivo tiene errores de validación:")
            for error in errores:
                st.write(error)
            st.session_state['demanda_validado'] = False

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {str(e)}")
        st.session_state['demanda_validado'] = False

st.markdown("---")

# =============================================================================
# ESTADO GENERAL
# =============================================================================

st.subheader("📋 Estado de Carga")

col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.get('parametros_validado', False):
        st.success("✅ Parámetros")
    else:
        st.warning("⏳ Parámetros")

with col2:
    if st.session_state.get('demanda_validado', False):
        st.success("✅ Demanda")
    else:
        st.warning("⏳ Demanda")

with col3:
    if (st.session_state.get('parametros_validado', False) and
        st.session_state.get('demanda_validado', False)):
        st.success("✅ Listo para ejecutar")
        st.info("👉 Ve a la página **Ejecutar Modelo** para continuar")
    else:
        st.info("⏳ Carga ambos archivos")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Sistema de Optimización de Cajas - Módulo de Carga de Archivos</p>
</div>
""", unsafe_allow_html=True)
