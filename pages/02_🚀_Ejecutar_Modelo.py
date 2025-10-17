"""Página para seleccionar planta y ejecutar el modelo de optimización."""

import streamlit as st
import pandas as pd
import subprocess
import sys
from run_model import run
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from styles.common_styles import configure_page
from utils import show_logo

# Configurar página
configure_page("Ejecutar Modelo", "🚀", "wide")

# Sidebar
with st.sidebar:
    show_logo()
    st.markdown("---")
    st.markdown("### 🚀 Ejecutar Modelo")
    st.info("Selecciona una planta y ejecuta la optimización")

st.title("🚀 Seleccionar Planta y Ejecutar Modelo")

st.markdown("""
### Ejecución del Modelo de Optimización

Selecciona una planta y ejecuta el modelo de optimización de cajas.
El sistema procesará los datos y generará la solución óptima.
""")

st.markdown("---")

# =============================================================================
# VERIFICAR QUE LOS ARCHIVOS ESTÉN CARGADOS
# =============================================================================

if not st.session_state.get('parametros_validado', False) or not st.session_state.get('demanda_validado', False):
    st.warning("⚠️ Primero debes cargar los archivos en la página **Cargar Archivos**")

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.get('parametros_validado', False):
            st.success("✅ Parámetros cargados")
        else:
            st.error("❌ Parámetros NO cargados")

    with col2:
        if st.session_state.get('demanda_validado', False):
            st.success("✅ Demanda cargada")
        else:
            st.error("❌ Demanda NO cargada")

    st.info("👈 Ve a la página **Cargar Archivos** para cargar los datos necesarios")
    st.stop()

# =============================================================================
# MOSTRAR ARCHIVOS CARGADOS
# =============================================================================

st.success("✅ Archivos cargados correctamente")

col1, col2 = st.columns(2)

with col1:
    st.info(f"📄 **Parámetros**: {st.session_state.get('parametros_nombre', 'N/A')}")

with col2:
    st.info(f"📄 **Demanda**: {st.session_state.get('demanda_nombre', 'N/A')}")

st.markdown("---")

# =============================================================================
# SELECTOR DE PLANTA
# =============================================================================

st.subheader("1️⃣ Seleccionar Planta")

# Obtener plantas disponibles desde session state
plantas_disponibles = []
if 'parametros_dict' in st.session_state:
    if 'Planta' in st.session_state['parametros_dict']:
        plantas_disponibles = st.session_state['parametros_dict']['Planta']['PLANTA'].tolist()

if plantas_disponibles:
    col1, col2 = st.columns([2, 1])

    with col1:
        planta_seleccionada = st.selectbox(
            "Selecciona la planta:",
            plantas_disponibles,
            key="planta_selector",
            help="Planta para la cual ejecutar el modelo de optimización"
        )

        # Guardar en session state
        st.session_state['planta_seleccionada'] = planta_seleccionada

    with col2:
        st.metric("Planta Seleccionada", planta_seleccionada)

    # Mostrar información de la planta
    with st.expander("📊 Información de la Planta", expanded=True):
        col_a, col_b, col_c, col_d = st.columns(4)

        # Máquinas
        if 'Disponibilidad Maquinas' in st.session_state['parametros_dict']:
            disp_df = st.session_state['parametros_dict']['Disponibilidad Maquinas']
            disp_planta = disp_df[disp_df['PLANTA'] == planta_seleccionada]
            with col_a:
                st.metric("Máquinas", disp_planta['MAQUINA'].nunique())

        # Días
        if 'Turnos' in st.session_state['parametros_dict']:
            turnos_df = st.session_state['parametros_dict']['Turnos']
            turnos_planta = turnos_df[turnos_df['PLANTA'] == planta_seleccionada]
            with col_b:
                st.metric("Días", turnos_planta['DIA'].nunique())

        # Tipos de caja
        if 'Productividad Máquina_Caja' in st.session_state['parametros_dict']:
            prod_df = st.session_state['parametros_dict']['Productividad Máquina_Caja']
            prod_planta = prod_df[prod_df['PLANTA'] == planta_seleccionada]
            with col_c:
                st.metric("Tipos de Caja", prod_planta['TIPO_CAJA'].nunique())

        # Registros de demanda
        if 'demanda_df' in st.session_state:
            demanda_df = st.session_state['demanda_df']
            if 'DES_PLANTA' in demanda_df.columns:
                demanda_planta = demanda_df[demanda_df['DES_PLANTA'] == planta_seleccionada]
                with col_d:
                    st.metric("Registros Demanda", len(demanda_planta))

        # Detalle de demanda
        if 'demanda_df' in st.session_state:
            demanda_df = st.session_state['demanda_df']
            if 'DES_PLANTA' in demanda_df.columns:
                demanda_planta = demanda_df[demanda_df['DES_PLANTA'] == planta_seleccionada]

                if len(demanda_planta) > 0:
                    st.markdown(f"**Demanda para {planta_seleccionada}:**")

                    col_dem1, col_dem2 = st.columns(2)

                    with col_dem1:
                        if 'cajas_asignadas' in demanda_planta.columns:
                            total_cajas = demanda_planta['cajas_asignadas'].sum()
                            st.write(f"- **Total cajas:** {total_cajas:,.0f}")

                    with col_dem2:
                        if 'DESC_ENVASE' in demanda_planta.columns:
                            tipos_envase = demanda_planta['DESC_ENVASE'].nunique()
                            st.write(f"- **Tipos de envase:** {tipos_envase}")
                else:
                    st.warning(f"⚠️ No hay datos de demanda para {planta_seleccionada}")

    st.markdown("---")

    # =============================================================================
    # EJECUTAR MODELO
    # =============================================================================

    st.subheader("2️⃣ Ejecutar Optimización")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

    with col_btn2:
        if st.button("▶️ Ejecutar Modelo de Optimización", type="primary", use_container_width=True):
            planta = st.session_state['planta_seleccionada']

            st.info(f"🔄 Iniciando optimización para planta: **{planta}**")

            # Contenedor de progreso
            progress_container = st.container()

            with progress_container:
                with st.spinner("Procesando datos y ejecutando modelo..."):
                    try:
                        # Ejecutar run_model.py
                        result = run(planta)

                        # Verificar resultado

                            # Guardar en session state
                        st.session_state['ultima_ejecucion'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state['modelo_ejecutado'] = True
                        st.session_state['ultima_planta'] = planta

                            # Verificar archivos de salida
                        if Path("solution.json").exists():
                            st.success("✅ solution.json generado")

                        if Path("log.txt").exists():
                            st.success("✅ log.txt generado")

                        st.balloons()
                        st.info("👉 Ve a la página **Resultados** para ver el análisis detallado")

                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")

    # Información del proceso
    with st.expander("ℹ️ ¿Qué hace el modelo?", expanded=False):
        st.markdown("""
        ### Proceso de Optimización

        1. **Procesamiento de Datos**
           - Filtra parámetros por planta seleccionada
           - Filtra demanda por planta seleccionada
           - Genera archivos CSV temporales

        2. **Empaquetado**
           - Crea archivo tar.gz con modelo y datos
           - Incluye scripts de optimización CPLEX

        3. **Ejecución en Watson ML**
           - Sube modelo a IBM Watson Machine Learning
           - Crea deployment
           - Ejecuta optimización con CPLEX
           - Descarga resultados

        4. **Resultados**
           - `solution.json`: Solución óptima
           - `log.txt`: Registro de ejecución

        **Tiempo estimado:** 2-5 minutos
        """)

else:
    st.error("❌ No se encontraron plantas en los parámetros")

# =============================================================================
# HISTORIAL
# =============================================================================

if st.session_state.get('ultima_ejecucion'):
    st.markdown("---")
    st.subheader("📋 Última Ejecución")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Fecha:** {st.session_state['ultima_ejecucion']}")

    with col2:
        st.info(f"**Planta:** {st.session_state.get('ultima_planta', 'N/A')}")

    with col3:
        if Path("solution.json").exists():
            st.success("✅ Resultados disponibles")
        else:
            st.warning("⚠️ Sin resultados")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Sistema de Optimización de Cajas - Módulo de Ejecución</p>
</div>
""", unsafe_allow_html=True)
