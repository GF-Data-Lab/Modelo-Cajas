import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from itertools import product
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from components.model_runner import ModelRunner

st.set_page_config(
    page_title="Optimización - Modelo Cajas",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Optimización del Modelo")
st.markdown("Configura y ejecuta el modelo de optimización de producción de cajas")

# Verificar que los datos estén cargados
if not st.session_state.get('datos_cargados', False):
    st.error("❌ No hay datos cargados. Ve a la página de **Configuración** primero.")
    st.stop()

params = st.session_state.parametros

# ==================== CONFIGURACIÓN DE DEMANDA ====================
st.header("📦 Configuración de Demanda")

with st.expander("ℹ️ Acerca de la Demanda", expanded=False):
    st.markdown("""
    Define la cantidad de cajas que necesitas producir para cada tipo de caja y cada día.

    - **Tipo de Caja**: Diferentes modelos/tamaños de cajas que produces
    - **Día**: Día de producción (1, 2, 3, etc.)
    - **Demanda**: Cantidad de cajas requeridas

    El modelo intentará satisfacer o superar esta demanda minimizando los tiempos de setup.
    """)

# Crear tabla editable para demanda
B = params.get('B', [])
D = params.get('D', [])

if not B or not D:
    st.error("No hay tipos de caja o días definidos en los parámetros")
    st.stop()

# Inicializar demanda en session state si no existe
if 'demanda_config' not in st.session_state:
    # Crear demanda por defecto
    demanda_rows = []
    for b in B:
        for d in D:
            demanda_rows.append({
                'TipoCaja': b,
                'Dia': d,
                'Demanda': 10.0  # Valor por defecto
            })
    st.session_state.demanda_config = pd.DataFrame(demanda_rows)

# Editor de demanda
st.subheader("Editar Demanda")

col1, col2 = st.columns([3, 1])

with col1:
    demanda_df = st.data_editor(
        st.session_state.demanda_config,
        use_container_width=True,
        hide_index=True,
        column_config={
            "TipoCaja": st.column_config.TextColumn("Tipo de Caja", disabled=True),
            "Dia": st.column_config.NumberColumn("Día", disabled=True),
            "Demanda": st.column_config.NumberColumn("Demanda", min_value=0, format="%.1f")
        },
        key="editor_demanda"
    )

with col2:
    st.metric("Total Items", len(demanda_df))
    st.metric("Demanda Total", f"{demanda_df['Demanda'].sum():.0f}")

    if st.button("🔄 Reset Demanda", use_container_width=True):
        del st.session_state.demanda_config
        st.rerun()

# Guardar cambios en demanda
st.session_state.demanda_config = demanda_df

st.markdown("---")

# ==================== PARÁMETROS DEL SOLVER ====================
st.header("⚙️ Parámetros del Solver")

col1, col2, col3 = st.columns(3)

with col1:
    time_limit = st.number_input(
        "Tiempo Límite (segundos)",
        min_value=10,
        max_value=600,
        value=60,
        step=10,
        help="Tiempo máximo de ejecución del solver"
    )

with col2:
    mip_gap = st.slider(
        "MIP Gap (%)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.5,
        help="Gap de optimalidad aceptable"
    ) / 100

with col3:
    tturn = st.number_input(
        "Duración Turno (horas)",
        min_value=1.0,
        max_value=24.0,
        value=8.0,
        step=0.5,
        help="Duración de cada turno en horas"
    )

# ==================== OPCIONES AVANZADAS ====================
with st.expander("🔬 Opciones Avanzadas", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        enforce_tipo = st.checkbox(
            "Forzar Compatibilidad Máquina-Caja",
            value=True,
            help="Si está activado, solo permite asignaciones con productividad > 0"
        )

    with col2:
        restrict_w = st.checkbox(
            "Restringir Variables W por Tipo",
            value=True,
            help="Reduce variables de setup considerando solo combinaciones compatibles"
        )

    tseg = st.number_input(
        "Duración Segmento (horas)",
        min_value=0.5,
        max_value=12.0,
        value=tturn / 2,
        step=0.5,
        help="Duración de cada segmento dentro de un turno. Por defecto: Turno/2"
    )

st.markdown("---")

# ==================== EJECUTAR OPTIMIZACIÓN ====================
st.header("🚀 Ejecutar Optimización")

# Resumen antes de ejecutar
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Máquinas:** {len(params['M'])}")
    st.info(f"**Días:** {len(params['D'])}")

with col2:
    st.info(f"**Tipos de Caja:** {len(params['B'])}")
    st.info(f"**Turnos:** {sum(len(v) for v in params['T_turnos'].values())}")

with col3:
    st.info(f"**Demanda Total:** {demanda_df['Demanda'].sum():.0f}")
    st.info(f"**Time Limit:** {time_limit}s")

# Botón de ejecución
if st.button("▶️ EJECUTAR MODELO", type="primary", use_container_width=True):

    # Convertir demanda de DataFrame a diccionario
    Dem = {}
    for _, row in demanda_df.iterrows():
        Dem[(row['TipoCaja'], row['Dia'])] = float(row['Demanda'])

    # Crear instancia del runner
    runner = ModelRunner()

    # Inicializar con los dataframes actuales
    if not runner.initialize_from_dataframes(st.session_state.dataframes):
        st.error("❌ Error al inicializar el modelo")
        st.stop()

    # Extraer parámetros
    params = runner.extract_parameters()
    if not params:
        st.error("❌ Error al extraer parámetros")
        st.stop()

    # Ejecutar optimización
    st.info("🔄 Ejecutando optimización... Esto puede tomar algunos minutos.")

    success, results = runner.build_and_solve(
        params=params,
        Dem=Dem,
        Tturn=tturn,
        enforce_tipo=enforce_tipo,
        Tseg=tseg,
        restrict_w_by_tipo=restrict_w,
        time_limit=time_limit,
        mip_gap=mip_gap
    )

    if success:
        # Guardar resultados en session state
        if 'soluciones' not in st.session_state:
            st.session_state.soluciones = []

        st.session_state.soluciones.append(results)
        st.session_state.ultima_solucion = results
        st.session_state.ultima_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.success("✅ ¡Optimización completada exitosamente!")

        # Mostrar resumen
        st.markdown("### 📊 Resumen de Resultados")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Objetivo (Setup)", f"{results['objetivo']} h")

        with col2:
            st.metric("Horas Producción", f"{results['total_produccion_h']} h")

        with col3:
            eficiencia = (results['total_produccion_h'] /
                         (results['total_produccion_h'] + results['total_setup_h']) * 100)
            st.metric("Eficiencia", f"{eficiencia:.1f}%")

        with col4:
            st.metric("Asignaciones", len(results['asignaciones']))

        st.info("👉 Ve a la página **📈 Resultados** para ver visualizaciones detalladas")

    else:
        st.error("❌ El modelo no encontró una solución factible. Intenta:")
        st.markdown("""
        - Reducir la demanda
        - Aumentar la disponibilidad de máquinas
        - Aumentar el tiempo límite del solver
        - Revisar la compatibilidad máquina-caja en la configuración
        """)

# ==================== HISTORIAL ====================
st.markdown("---")
st.header("📜 Historial de Ejecuciones")

if st.session_state.get('soluciones'):
    st.success(f"Total de ejecuciones: {len(st.session_state.soluciones)}")

    # Tabla de historial
    historial = []
    for i, sol in enumerate(st.session_state.soluciones):
        historial.append({
            'ID': i + 1,
            'Fecha': sol.get('timestamp', 'N/A'),
            'Objetivo': f"{sol['objetivo']} h",
            'Eficiencia': f"{(sol['total_produccion_h'] / (sol['total_produccion_h'] + sol['total_setup_h']) * 100):.1f}%",
            'Asignaciones': len(sol['asignaciones'])
        })

    df_historial = pd.DataFrame(historial)
    st.dataframe(df_historial, use_container_width=True, hide_index=True)

    if st.button("🗑️ Limpiar Historial"):
        st.session_state.soluciones = []
        st.session_state.ultima_solucion = None
        st.rerun()

else:
    st.info("No hay ejecuciones previas")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💡 Los resultados se guardan en la sesión actual. Exporta en la página de Exportar.</p>
</div>
""", unsafe_allow_html=True)
