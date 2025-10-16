"""Página para visualizar resultados y análisis del modelo."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from styles.common_styles import configure_page
from utils import show_logo

# Configurar página
configure_page("Resultados", "📊", "wide")

# Sidebar
with st.sidebar:
    show_logo()
    st.markdown("---")
    st.markdown("### 📊 Resultados")
    st.info("Análisis y visualización de resultados")

st.title("📊 Resultados y Análisis")

st.markdown("""
### Visualización de Resultados del Modelo de Optimización

Análisis detallado de la solución óptima generada por el modelo.
""")

st.markdown("---")

# =============================================================================
# VERIFICAR QUE EXISTAN RESULTADOS
# =============================================================================

solution_path = Path("solution.json")
log_path = Path("log.txt")

if not solution_path.exists():
    st.warning("⚠️ No se encontraron resultados del modelo")

    st.info("""
    ### ¿Cómo generar resultados?

    1. Ve a la página **Cargar Archivos** y sube los datos
    2. Ve a la página **Ejecutar Modelo**
    3. Selecciona una planta y ejecuta el modelo
    4. Los resultados aparecerán aquí automáticamente
    """)

    if st.session_state.get('ultima_ejecucion'):
        st.warning(f"Última ejecución: {st.session_state['ultima_ejecucion']}")
        st.warning(f"Planta: {st.session_state.get('ultima_planta', 'N/A')}")

    st.stop()

# =============================================================================
# CARGAR RESULTADOS
# =============================================================================

# Cargar o recuperar de session_state
if 'solution_data' not in st.session_state or st.button("🔄 Recargar resultados"):
    try:
        with open(solution_path, 'r', encoding='utf-8') as f:
            solution = json.load(f)

        # Guardar en session_state
        st.session_state.solution_data = solution
        st.success("✅ Resultados cargados correctamente")

    except Exception as e:
        st.error(f"❌ Error al cargar solution.json: {str(e)}")
        st.stop()
else:
    solution = st.session_state.solution_data
    st.info("📊 Mostrando resultados guardados en la sesión")

# =============================================================================
# INFORMACIÓN GENERAL
# =============================================================================

st.subheader("📋 Información General")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.get('ultima_planta'):
        st.metric("Planta", st.session_state['ultima_planta'])
    else:
        st.metric("Planta", "N/A")

with col2:
    if st.session_state.get('ultima_ejecucion'):
        st.metric("Fecha Ejecución", st.session_state['ultima_ejecucion'])
    else:
        st.metric("Fecha Ejecución", "N/A")

with col3:
    # Estado de la solución
    if 'CPLEXSolution' in solution:
        status = solution['CPLEXSolution'].get('header', {}).get('solutionStatusString', 'N/A')
        st.metric("Estado", status)
    else:
        st.metric("Estado", "N/A")

with col4:
    # Función objetivo
    if 'CPLEXSolution' in solution:
        obj_value = solution['CPLEXSolution'].get('header', {}).get('objectiveValue', 'N/A')
        if obj_value != 'N/A':
            st.metric("Valor Objetivo", f"{float(obj_value):.2f}")
        else:
            st.metric("Valor Objetivo", "N/A")
    else:
        st.metric("Valor Objetivo", "N/A")

st.markdown("---")

# =============================================================================
# PROCESAR DATOS DE LA SOLUCIÓN
# =============================================================================

@st.cache_data
def procesar_solucion(sol_dict):
    """Procesa el solution.json y extrae DataFrames."""

    data = {
        'variables': [],
        'constraints': [],
        'kpis': {}
    }

    try:
        if 'CPLEXSolution' in sol_dict:
            cplex_sol = sol_dict['CPLEXSolution']

            # Extraer variables
            if 'variables' in cplex_sol:
                vars_data = cplex_sol['variables']

                # Si variables es un diccionario con clave 'variable'
                if isinstance(vars_data, dict) and 'variable' in vars_data:
                    vars_data = vars_data['variable']
                    if isinstance(vars_data, dict):
                        vars_data = [vars_data]
                # Si variables es directamente una lista
                elif isinstance(vars_data, list):
                    pass  # Ya es una lista
                else:
                    vars_data = []

                for var in vars_data:
                    # Manejar ambos formatos: con @ o sin @
                    nombre = var.get('name', var.get('@name', ''))
                    valor = var.get('value', var.get('@value', 0))
                    index = var.get('index', var.get('@index', ''))

                    data['variables'].append({
                        'nombre': nombre,
                        'valor': float(valor),
                        'index': str(index)
                    })

            # Extraer KPIs del header
            header = cplex_sol.get('header', {})
            data['kpis'] = {
                'objective_value': header.get('objectiveValue', 0),
                'solve_time': header.get('solutionTime', header.get('solveTime', 0)),
                'status': header.get('solutionStatusString', header.get('status', 'N/A'))
            }

    except Exception as e:
        st.error(f"Error procesando solución: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

    return data

# Procesar solución
data_procesada = procesar_solucion(solution)

# Guardar en session_state
st.session_state.data_procesada = data_procesada

# Convertir a DataFrame
if data_procesada['variables']:
    df_variables = pd.DataFrame(data_procesada['variables'])

    # Guardar DataFrame completo en session_state
    st.session_state.df_variables_completo = df_variables.copy()

    # Filtrar valores significativos
    df_variables = df_variables[df_variables['valor'] > 0.01]
    st.session_state.df_variables = df_variables

    st.success(f"✅ {len(data_procesada['variables'])} variables procesadas, {len(df_variables)} con valor significativo (>0.01)")
else:
    df_variables = pd.DataFrame()
    st.warning("⚠️ No se encontraron variables en la solución")

# =============================================================================
# MÉTRICAS CLAVE (KPIs)
# =============================================================================

st.subheader("📈 Métricas Clave")

if data_procesada['kpis']:
    col1, col2, col3 = st.columns(3)

    with col1:
        obj_val = data_procesada['kpis'].get('objective_value', 0)
        if obj_val:
            st.metric("Función Objetivo", f"{float(obj_val):.2f}", help="Valor de la función objetivo (tiempo total de setup)")
        else:
            st.metric("Función Objetivo", "N/A")

    with col2:
        solve_time = data_procesada['kpis'].get('solve_time', 0)
        if solve_time:
            st.metric("Tiempo de Solución", f"{float(solve_time):.2f} s", help="Tiempo que tomó resolver el modelo")
        else:
            st.metric("Tiempo de Solución", "N/A")

    with col3:
        if not df_variables.empty:
            n_vars_activas = len(df_variables)
            st.metric("Variables Activas", n_vars_activas, help="Número de variables de decisión con valor > 0")
        else:
            st.metric("Variables Activas", 0)

st.markdown("---")

# =============================================================================
# TABLA DE RESULTADOS PRINCIPAL
# =============================================================================

st.subheader("📋 Tabla de Resultados - Variables de Decisión")

if not df_variables.empty:

    # Selector de vista
    col_vista1, col_vista2 = st.columns(2)
    with col_vista1:
        mostrar_todas = st.checkbox("Mostrar todas las variables (incluye valores pequeños)", value=False)
    with col_vista2:
        if mostrar_todas:
            st.info(f"Mostrando {len(st.session_state.df_variables_completo)} variables totales")
        else:
            st.info(f"Mostrando {len(df_variables)} variables con valor > 0.01")

    # Seleccionar DataFrame según opción
    df_mostrar = st.session_state.df_variables_completo if mostrar_todas else df_variables

    # Ordenar por valor descendente
    df_mostrar_sorted = df_mostrar.sort_values('valor', ascending=False).reset_index(drop=True)

    # Agregar columna de número de fila
    df_display = df_mostrar_sorted.copy()
    df_display.insert(0, '#', range(1, len(df_display) + 1))

    # Formatear valores
    df_display['valor'] = df_display['valor'].apply(lambda x: f"{x:.6f}")

    # Mostrar tabla con scroll
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )

    # Botones de descarga
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_filtered = df_mostrar_sorted.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar tabla actual (CSV)",
            csv_filtered,
            f"variables_solucion_{'completo' if mostrar_todas else 'filtrado'}.csv",
            "text/csv",
            key='download-table-csv'
        )

    with col_d2:
        csv_completo = st.session_state.df_variables_completo.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar todas las variables (CSV)",
            csv_completo,
            "variables_solucion_completo.csv",
            "text/csv",
            key='download-all-csv'
        )

    st.markdown("---")

else:
    st.info("No hay variables para mostrar en la tabla")

# =============================================================================
# ANÁLISIS DE VARIABLES
# =============================================================================

st.subheader("🔍 Análisis de Variables de Decisión")

if not df_variables.empty:

    # Filtros
    col_f1, col_f2 = st.columns(2)

    with col_f1:
        search_term = st.text_input("🔍 Buscar variable:", "", help="Filtra por nombre de variable")

    with col_f2:
        top_n = st.slider("Top N variables:", 10, 100, 50, step=10, help="Número de variables a mostrar")

    # Aplicar filtros
    df_filtered = df_variables.copy()
    if search_term:
        df_filtered = df_filtered[df_filtered['nombre'].str.contains(search_term, case=False, na=False)]

    # Ordenar por valor
    df_filtered = df_filtered.sort_values('valor', ascending=False).head(top_n)

    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📊 Gráfico", "📋 Tabla", "📈 Estadísticas"])

    with tab1:
        if len(df_filtered) > 0:
            # Gráfico de barras
            fig = px.bar(
                df_filtered.head(20),
                x='nombre',
                y='valor',
                title=f'Top 20 Variables con Mayor Valor',
                labels={'nombre': 'Variable', 'valor': 'Valor'},
                color='valor',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para mostrar")

    with tab2:
        # Tabla detallada
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True
        )

        # Botón de descarga
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar CSV",
            csv,
            "variables_solucion.csv",
            "text/csv",
            key='download-csv'
        )

    with tab3:
        # Estadísticas descriptivas
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("**Estadísticas de Valores:**")
            stats = df_variables['valor'].describe()
            st.dataframe(stats.to_frame('Valor'), use_container_width=True)

        with col_s2:
            st.markdown("**Distribución:**")

            # Histograma
            fig_hist = px.histogram(
                df_variables,
                x='valor',
                nbins=30,
                title='Distribución de Valores de Variables',
                labels={'valor': 'Valor', 'count': 'Frecuencia'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)

else:
    st.info("No hay variables para analizar")

st.markdown("---")

# =============================================================================
# ANÁLISIS POR TIPO DE VARIABLE
# =============================================================================

st.subheader("📦 Análisis por Tipo de Variable")

if not df_variables.empty:

    # Clasificar variables por prefijo
    df_variables['tipo'] = df_variables['nombre'].str.extract(r'^([a-zA-Z]+)')[0]

    # Contar por tipo
    tipo_counts = df_variables.groupby('tipo').agg({
        'valor': ['count', 'sum', 'mean']
    }).reset_index()
    tipo_counts.columns = ['Tipo', 'Cantidad', 'Suma', 'Promedio']

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        # Gráfico de pastel
        fig_pie = px.pie(
            tipo_counts,
            values='Cantidad',
            names='Tipo',
            title='Distribución de Variables por Tipo',
            hole=0.3
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_t2:
        # Tabla resumen
        st.markdown("**Resumen por Tipo:**")
        st.dataframe(tipo_counts, use_container_width=True, hide_index=True)

st.markdown("---")

# =============================================================================
# LOG DEL SOLVER
# =============================================================================

st.subheader("📝 Log del Solver")

if log_path.exists():
    with st.expander("Ver log completo", expanded=False):
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()

            st.code(log_content, language='text')

        except Exception as e:
            st.error(f"Error al leer log: {str(e)}")
else:
    st.warning("⚠️ No se encontró el archivo log.txt")

st.markdown("---")

# =============================================================================
# RESUMEN EJECUTIVO
# =============================================================================

st.subheader("📄 Resumen Ejecutivo")

with st.expander("Ver resumen completo", expanded=True):

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("### 📊 Modelo")
        if not df_variables.empty:
            st.write(f"- **Variables de decisión:** {len(data_procesada['variables'])}")
            st.write(f"- **Variables activas:** {len(df_variables)}")
            st.write(f"- **Tipos de variables:** {df_variables['tipo'].nunique() if 'tipo' in df_variables.columns else 'N/A'}")

        st.markdown("### ⏱️ Ejecución")
        if data_procesada['kpis']:
            st.write(f"- **Tiempo de solución:** {data_procesada['kpis'].get('solve_time', 'N/A')} s")
            st.write(f"- **Estado:** {data_procesada['kpis'].get('status', 'N/A')}")

    with col_r2:
        st.markdown("### 🎯 Resultados")
        if data_procesada['kpis']:
            st.write(f"- **Función objetivo:** {data_procesada['kpis'].get('objective_value', 'N/A')}")

        if st.session_state.get('ultima_planta'):
            st.markdown("### 🏭 Planta")
            st.write(f"- **Nombre:** {st.session_state['ultima_planta']}")
            st.write(f"- **Fecha ejecución:** {st.session_state.get('ultima_ejecucion', 'N/A')}")

# =============================================================================
# DATOS CRUDOS
# =============================================================================

st.markdown("---")

with st.expander("🔧 Ver datos crudos (JSON)", expanded=False):
    st.json(solution)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Sistema de Optimización de Cajas - Módulo de Resultados</p>
</div>
""", unsafe_allow_html=True)
