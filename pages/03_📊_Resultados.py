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
from mapeo_nombres import obtener_mapeador

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

# Inicializar mapeador de nombres
try:
    mapeador = obtener_mapeador()
    mapeo_disponible = True
    st.success(f"✅ Mapeo de nombres cargado: {len(mapeador.obtener_mapeo_maquinas())} máquinas, {len(mapeador.obtener_mapeo_cajas())} tipos de caja")
except Exception as e:
    st.warning(f"⚠️ No se pudo cargar el mapeo de nombres: {e}")
    mapeador = None
    mapeo_disponible = False

# Procesar solución
data_procesada = procesar_solucion(solution)

# Guardar en session_state
st.session_state.data_procesada = data_procesada
st.session_state.mapeador = mapeador

# Convertir a DataFrame
if data_procesada['variables']:
    df_variables = pd.DataFrame(data_procesada['variables'])

    # Agregar columna con descripción legible si hay mapeo
    if mapeo_disponible and mapeador:
        df_variables['descripcion'] = df_variables['nombre'].apply(
            lambda x: mapeador.mapear_variable_completa(x)
        )

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
# =============================================================================
# TABLA DETALLADA DE VARIABLES y_ (horas por Máquina/Caja/Día/Turno/Segmento)
# =============================================================================
st.subheader("🕒 Cronograma Diario")

import re

def parsear_y_variable(nombre: str):
    """
    Parseo robusto de nombres tipo:
    y_M11_MASTER 2 X 2,5 KILOS_2_1_1
    y_M6_FONDO 5 KILOS_3_1_2

    Patrón: y_<MAQUINA>_<NOMBRE_CAJA>_<DIA>_<TURNO>_<SEGMENTO>
    Donde <NOMBRE_CAJA> puede contener espacios y comas.
    """
    # Regex: (1) maquina (2) caja (greedy) (3) dia (4) turno (5) segmento
    patron = r"^y_([^_]+)_(.+)_(\d+)_(\d+)_(\d+)$"
    m = re.match(patron, nombre)
    if not m:
        return None
    maquina, caja, dia, turno, segmento = m.groups()
    return {
        "maquina": maquina.strip(),
        "caja": caja.strip(),
        "dia": int(dia),
        "turno": int(turno),
        "segmento": int(segmento),
    }

if not df_variables.empty:
    # Tomamos todas las y_ (si marcaste "mostrar todas", usa df_mostrar_sorted si quieres)
    df_y = st.session_state.df_variables_completo.copy()
    df_y = df_y[df_y["nombre"].str.startswith("y_")].copy()

    if df_y.empty:
        st.info("No se encontraron variables y_ en la solución.")
    else:
        # Parsear columnas
        parsed = df_y["nombre"].apply(parsear_y_variable)
        df_y = df_y[parsed.notna()].copy()
        parsed_dicts = parsed[parsed.notna()]

        df_y["maquina"]  = parsed_dicts.apply(lambda d: d["maquina"])
        df_y["caja"]     = parsed_dicts.apply(lambda d: d["caja"])
        df_y["dia"]      = parsed_dicts.apply(lambda d: d["dia"])
        df_y["turno"]    = parsed_dicts.apply(lambda d: d["turno"])
        df_y["segmento"] = parsed_dicts.apply(lambda d: d["segmento"])

        # Mapear nombres legibles si hay mapeador
        if mapeo_disponible and mapeador:
            df_y["maquina_nombre"] = df_y["maquina"].apply(lambda x: mapeador.mapear_maquina(x) or x)
            df_y["caja_nombre"]    = df_y["caja"].apply(lambda x: mapeador.mapear_caja(x) or x)
        else:
            df_y["maquina_nombre"] = df_y["maquina"]
            df_y["caja_nombre"]    = df_y["caja"]

        # Renombrar y ordenar columnas para la tabla final
        df_y_tabla = df_y.rename(columns={
            "valor": "horas"
        })[
            ["maquina", "maquina_nombre", "caja", "caja_nombre", "dia", "turno", "segmento", "horas", "nombre"]
        ].sort_values(by=["dia", "turno", "maquina_nombre", "caja_nombre", "segmento"]).reset_index(drop=True)

        # Formatear horas a 6 decimales (o lo que prefieras)
        df_y_tabla["horas"] = df_y_tabla["horas"].astype(float).round(6)

        # Mostrar
        st.dataframe(
            df_y_tabla,
            use_container_width=True,
            hide_index=True,
            column_config={
                "maquina": st.column_config.TextColumn("Código Máquina", width="small"),
                "maquina_nombre": st.column_config.TextColumn("Máquina", width="medium"),
                "caja": st.column_config.TextColumn("Código Caja", width="medium"),
                "caja_nombre": st.column_config.TextColumn("Caja", width="large"),
                "dia": st.column_config.NumberColumn("Día", width="small"),
                "turno": st.column_config.NumberColumn("Turno", width="small"),
                "segmento": st.column_config.NumberColumn("Segmento", width="small"),
                "horas": st.column_config.NumberColumn("Horas", width="small", format="%.6f"),
                "nombre": st.column_config.TextColumn("Variable (raw)", width="large"),
            }
        )

        # Descarga
        csv_y = df_y_tabla.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Descargar variables y_ (CSV)",
            csv_y,
            "variables_y_detalle.csv",
            "text/csv",
            key="download-y-csv"
        )

        # (Opcional) Resumen rápido por Máquina/Caja
        with st.expander("📦 Resumen por Máquina × Caja (suma de horas)", expanded=False):
            resumen = (
                df_y_tabla.groupby(["maquina_nombre", "caja_nombre"], as_index=False)["horas"]
                .sum()
                .sort_values(["maquina_nombre", "horas"], ascending=[True, False])
            )
            st.dataframe(resumen, use_container_width=True, hide_index=True)
else:
    st.info("No hay variables para construir la tabla de y_.")

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
# INTERPRETACIÓN DE RESULTADOS
# =============================================================================

st.subheader("🔍 Interpretación de Resultados")

with st.expander("📖 Guía de Interpretación", expanded=True):
    st.markdown("""
    ### Tipos de Variables en la Solución

    El modelo de optimización utiliza dos tipos de variables principales:

    #### 🔹 Variables de Asignación (x)
    **Formato:** `x_mX_cY_D_T_S`
    - **Significado:** Indica si una máquina produce un tipo de caja en un día y turno específico
    - **Valor:** 1.0 = Asignado, 0.0 = No asignado
    - **Componentes:**
      - `mX`: Máquina (m1, m2, m3, ...)
      - `cY`: Tipo de caja (c1, c2, c3, ...)
      - `D`: Día de planificación (1-7)
      - `T`: Turno del día (1, 2, 3, ...)
      - `S`: Secuencia o periodo adicional

    **Ejemplo:** `x_m1_c2_3_4_1 = 1.0`
    - Máquina 1 (m1) está asignada para producir Caja 2 (c2) el Día 3, Turno 4

    #### 🔹 Variables de Producción/Tiempo (y)
    **Formato:** `y_mX_cY_D_T_S`
    - **Significado:** Cantidad o tiempo de producción de un tipo de caja
    - **Valor:** Números decimales (horas, cajas, o porcentaje del turno)
    - **Componentes:** Igual que variables x

    **Ejemplo:** `y_m2_c1_5_2_1 = 0.0391`
    - En Máquina 2, Caja 1, Día 5, Turno 2 se producen/utilizan 0.0391 unidades (horas/cajas)

    ---

    ### 📊 Objetivo del Modelo

    El modelo busca **minimizar el tiempo total de setup** (cambios de configuración entre tipos de caja),
    mientras se cumple con toda la demanda planificada y se respetan las capacidades de las máquinas.

    #### Restricciones consideradas:
    - ✅ **Demanda:** Toda la demanda de cajas debe ser satisfecha
    - ✅ **Capacidad:** Las máquinas no pueden exceder su tiempo disponible por turno
    - ✅ **Disponibilidad:** Solo se usan máquinas disponibles en cada día
    - ✅ **Productividad:** Se respetan las tasas de producción específicas de cada máquina-caja
    - ✅ **Setup:** Se minimizan los cambios de tipo de caja en cada máquina
    """)

st.markdown("---")

# =============================================================================
# RESUMEN EJECUTIVO MEJORADO
# =============================================================================

st.subheader("📊 Resumen Ejecutivo del Plan de Producción")

if not df_variables.empty:

    # Analizar variables de asignación (x)
    df_asignaciones = df_variables[df_variables['nombre'].str.startswith('x_')].copy()
    df_produccion = df_variables[df_variables['nombre'].str.startswith('y_')].copy()

    # Extraer información de las variables
    def parsear_variable(nombre):
        """Extrae componentes de la variable."""
        partes = nombre.split('_')
        if len(partes) >= 5:
            return {
                'tipo': partes[0],
                'maquina': partes[1],
                'caja': partes[2],
                'dia': partes[3],
                'turno': partes[4] if len(partes) > 4 else '1'
            }
        return None

    # Aplicar parsing a asignaciones
    if len(df_asignaciones) > 0:
        df_asignaciones['parsed'] = df_asignaciones['nombre'].apply(parsear_variable)
        df_asignaciones = df_asignaciones[df_asignaciones['parsed'].notna()].copy()

        # Expandir columnas
        df_asignaciones['maquina'] = df_asignaciones['parsed'].apply(lambda x: x['maquina'] if x else None)
        df_asignaciones['caja'] = df_asignaciones['parsed'].apply(lambda x: x['caja'] if x else None)
        df_asignaciones['dia'] = df_asignaciones['parsed'].apply(lambda x: x['dia'] if x else None)
        df_asignaciones['turno'] = df_asignaciones['parsed'].apply(lambda x: x['turno'] if x else None)

        # Agregar nombres reales si hay mapeo disponible
        if mapeo_disponible and mapeador:
            df_asignaciones['maquina_nombre'] = df_asignaciones['maquina'].apply(
                lambda x: mapeador.mapear_maquina(x) if x else x
            )
            df_asignaciones['caja_nombre'] = df_asignaciones['caja'].apply(
                lambda x: mapeador.mapear_caja(x) if x else x
            )
            df_asignaciones['dia_nombre'] = df_asignaciones['dia'].apply(
                lambda x: mapeador.mapear_dia(x) if x else x
            )

        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            n_maquinas = df_asignaciones['maquina'].nunique()
            st.metric("🏭 Máquinas Utilizadas", n_maquinas)

        with col2:
            n_cajas = df_asignaciones['caja'].nunique()
            st.metric("📦 Tipos de Caja", n_cajas)

        with col3:
            n_dias = df_asignaciones['dia'].nunique()
            st.metric("📅 Días Programados", n_dias)

        with col4:
            n_asignaciones = len(df_asignaciones)
            st.metric("🔄 Asignaciones Totales", n_asignaciones)

        st.markdown("---")

        # Análisis por máquina
        st.markdown("### 🏭 Utilización por Máquina")

        # Usar nombres reales si están disponibles
        grupo_maquina = 'maquina_nombre' if 'maquina_nombre' in df_asignaciones.columns else 'maquina'

        asignaciones_por_maquina = df_asignaciones.groupby(grupo_maquina).agg({
            'nombre': 'count',
            'caja': lambda x: x.nunique(),
            'dia': lambda x: x.nunique()
        }).reset_index()
        asignaciones_por_maquina.columns = ['Máquina', 'Total Asignaciones', 'Tipos de Caja', 'Días Trabajados']

        st.dataframe(asignaciones_por_maquina, use_container_width=True, hide_index=True)

        # Gráfico de asignaciones por máquina
        fig_maquinas = px.bar(
            asignaciones_por_maquina,
            x='Máquina',
            y='Total Asignaciones',
            title='Asignaciones por Máquina',
            color='Total Asignaciones',
            color_continuous_scale='Viridis',
            text='Total Asignaciones'
        )
        fig_maquinas.update_traces(textposition='outside')
        fig_maquinas.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_maquinas, use_container_width=True)

        st.markdown("---")

        # Análisis por día
        st.markdown("### 📅 Programación por Día")

        asignaciones_por_dia = df_asignaciones.groupby('dia').agg({
            'nombre': 'count',
            'maquina': lambda x: x.nunique(),
            'caja': lambda x: x.nunique()
        }).reset_index()
        asignaciones_por_dia.columns = ['Día', 'Total Asignaciones', 'Máquinas Activas', 'Tipos de Caja']
        asignaciones_por_dia = asignaciones_por_dia.sort_values('Día')

        # Gráfico de líneas por día
        fig_dias = go.Figure()
        fig_dias.add_trace(go.Scatter(
            x=asignaciones_por_dia['Día'],
            y=asignaciones_por_dia['Total Asignaciones'],
            mode='lines+markers',
            name='Asignaciones',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        fig_dias.add_trace(go.Scatter(
            x=asignaciones_por_dia['Día'],
            y=asignaciones_por_dia['Máquinas Activas'],
            mode='lines+markers',
            name='Máquinas Activas',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=10),
            yaxis='y2'
        ))
        fig_dias.update_layout(
            title='Actividad de Producción por Día',
            xaxis_title='Día',
            yaxis_title='Asignaciones',
            yaxis2=dict(title='Máquinas', overlaying='y', side='right'),
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_dias, use_container_width=True)

        st.dataframe(asignaciones_por_dia, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Análisis por tipo de caja
        st.markdown("### 📦 Producción por Tipo de Caja")

        # Usar nombres reales si están disponibles
        grupo_caja = 'caja_nombre' if 'caja_nombre' in df_asignaciones.columns else 'caja'

        asignaciones_por_caja = df_asignaciones.groupby(grupo_caja).agg({
            'nombre': 'count',
            'maquina': lambda x: x.nunique(),
            'dia': lambda x: x.nunique()
        }).reset_index()
        asignaciones_por_caja.columns = ['Tipo de Caja', 'Total Asignaciones', 'Máquinas Usadas', 'Días de Producción']

        st.dataframe(asignaciones_por_caja, use_container_width=True, hide_index=True)

        # Gráfico de barras por tipo de caja
        fig_cajas = px.bar(
            asignaciones_por_caja,
            x='Tipo de Caja',
            y='Total Asignaciones',
            title='Asignaciones por Tipo de Caja',
            color='Máquinas Usadas',
            color_continuous_scale='Teal',
            text='Total Asignaciones'
        )
        fig_cajas.update_traces(textposition='outside')
        fig_cajas.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_cajas, use_container_width=True)

        st.markdown("---")

        # Matriz de asignación Máquina-Caja
        st.markdown("### 🔄 Matriz de Asignación: Máquina × Tipo de Caja")

        # Usar nombres reales si están disponibles
        col_maquina_heatmap = 'maquina_nombre' if 'maquina_nombre' in df_asignaciones.columns else 'maquina'
        col_caja_heatmap = 'caja_nombre' if 'caja_nombre' in df_asignaciones.columns else 'caja'

        matriz_maquina_caja = df_asignaciones.groupby([col_maquina_heatmap, col_caja_heatmap]).size().reset_index(name='asignaciones')
        matriz_pivot = matriz_maquina_caja.pivot(index=col_maquina_heatmap, columns=col_caja_heatmap, values='asignaciones').fillna(0)

        fig_heatmap = px.imshow(
            matriz_pivot,
            labels=dict(x="Tipo de Caja", y="Máquina", color="Asignaciones"),
            title="Mapa de Calor: Asignaciones Máquina × Caja",
            color_continuous_scale='YlOrRd',
            text_auto=True
        )
        fig_heatmap.update_layout(
            height=600,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.info("""
        **💡 Interpretación del mapa de calor:**
        - Valores más altos (rojo) indican que esa máquina produce frecuentemente ese tipo de caja
        - Valores bajos (amarillo) indican producción ocasional
        - Casillas en blanco = sin asignaciones
        - Este mapa ayuda a identificar qué máquinas son especializadas en ciertos tipos de caja
        """)

    else:
        st.warning("No se encontraron variables de asignación (x_) en los resultados")

else:
    st.info("No hay datos suficientes para generar el resumen ejecutivo")

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

    # Reorganizar columnas para mostrar descripción si está disponible
    if 'descripcion' in df_display.columns:
        # Colocar descripción después del nombre
        cols = df_display.columns.tolist()
        cols_reordenadas = ['#', 'nombre', 'descripcion', 'valor']
        # Agregar cualquier otra columna que no hayamos especificado
        for col in cols:
            if col not in cols_reordenadas:
                cols_reordenadas.append(col)
        df_display = df_display[cols_reordenadas]

    # Formatear valores
    df_display['valor'] = df_display['valor'].apply(lambda x: f"{x:.6f}" if isinstance(x, (int, float)) else x)

    # Mostrar tabla con scroll
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn("#", width="small"),
            "nombre": st.column_config.TextColumn("Código Variable", width="medium"),
            "descripcion": st.column_config.TextColumn("Descripción", width="large"),
            "valor": st.column_config.TextColumn("Valor", width="small"),
        } if 'descripcion' in df_display.columns else None
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
