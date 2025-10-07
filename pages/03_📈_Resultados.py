import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from components.visualizations import Visualizations

st.set_page_config(
    page_title="Resultados - Modelo Cajas",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Resultados de la Optimización")
st.markdown("Visualiza y analiza los resultados del modelo de optimización")

# Verificar que haya resultados
if not st.session_state.get('ultima_solucion'):
    st.warning("⚠️ No hay resultados disponibles. Ejecuta el modelo en la página de **Optimización** primero.")
    st.stop()

results = st.session_state.ultima_solucion

# ==================== KPIs PRINCIPALES ====================
st.header("🎯 Indicadores Clave (KPIs)")

Visualizations.display_kpis(results)

st.markdown("---")

# ==================== TABS PARA DIFERENTES VISTAS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visualizaciones",
    "📋 Asignaciones",
    "📦 Cumplimiento Demanda",
    "⚙️ Setup"
])

# ==================== TAB 1: VISUALIZACIONES ====================
with tab1:
    st.subheader("Visualizaciones Interactivas")

    # Gráfico de Gantt
    with st.container():
        st.markdown("### 📅 Diagrama de Gantt - Asignaciones")
        gantt = Visualizations.create_gantt_chart(results['asignaciones'])
        if gantt:
            st.plotly_chart(gantt, use_container_width=True)
        else:
            st.info("No hay asignaciones para mostrar")

    st.markdown("---")

    # Dos columnas para gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔥 Utilización de Máquinas")
        heatmap = Visualizations.create_utilization_heatmap(results['utilizacion'])
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True)

    with col2:
        st.markdown("### ⏱️ Setup por Máquina")
        bar_chart = Visualizations.create_setup_bar_chart(results['setups'])
        if bar_chart:
            st.plotly_chart(bar_chart, use_container_width=True)

    st.markdown("---")

    # Más gráficos
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 📦 Demanda vs Producción")
        demand_chart = Visualizations.create_demand_fulfillment_chart(results['demanda'])
        if demand_chart:
            st.plotly_chart(demand_chart, use_container_width=True)

    with col4:
        st.markdown("### 🥧 Distribución de Tiempo")
        pie_chart = Visualizations.create_machine_productivity_pie(results['utilizacion'])
        if pie_chart:
            st.plotly_chart(pie_chart, use_container_width=True)

    st.markdown("---")

    # Timeline de producción
    with st.container():
        st.markdown("### 📈 Producción a lo Largo del Tiempo")
        timeline = Visualizations.create_production_timeline(results['asignaciones'])
        if timeline:
            st.plotly_chart(timeline, use_container_width=True)

# ==================== TAB 2: ASIGNACIONES ====================
with tab2:
    st.subheader("Tabla de Asignaciones Detallada")

    if results['asignaciones']:
        Visualizations.display_asignaciones_table(results['asignaciones'])

        # Descargar CSV
        df_asignaciones = pd.DataFrame(results['asignaciones'])
        csv = df_asignaciones.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Descargar Asignaciones (CSV)",
            data=csv,
            file_name="asignaciones.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No hay asignaciones para mostrar")

    # Estadísticas agregadas
    if results['asignaciones']:
        st.markdown("---")
        st.subheader("📊 Estadísticas Agregadas")

        df = pd.DataFrame(results['asignaciones'])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Por Máquina")
            stats_maquina = df.groupby('Maquina').agg({
                'Horas': 'sum',
                'Cajas': 'sum'
            }).reset_index()
            st.dataframe(stats_maquina, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("#### Por Tipo de Caja")
            stats_caja = df.groupby('TipoCaja').agg({
                'Horas': 'sum',
                'Cajas': 'sum'
            }).reset_index()
            st.dataframe(stats_caja, use_container_width=True, hide_index=True)

# ==================== TAB 3: CUMPLIMIENTO DEMANDA ====================
with tab3:
    st.subheader("Cumplimiento de Demanda")

    if results['demanda']:
        Visualizations.display_demanda_table(results['demanda'])

        # Descargar CSV
        df_demanda = pd.DataFrame(results['demanda'])
        csv_demanda = df_demanda.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Descargar Demanda (CSV)",
            data=csv_demanda,
            file_name="cumplimiento_demanda.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Análisis de cumplimiento
        st.markdown("---")
        st.subheader("📊 Análisis de Cumplimiento")

        col1, col2, col3 = st.columns(3)

        with col1:
            cumplimiento_100 = len([d for d in results['demanda'] if d['Cumplimiento'] >= 100])
            st.metric("Cumplimiento 100%", f"{cumplimiento_100}/{len(results['demanda'])}")

        with col2:
            cumplimiento_promedio = sum(d['Cumplimiento'] for d in results['demanda']) / len(results['demanda'])
            st.metric("Cumplimiento Promedio", f"{cumplimiento_promedio:.1f}%")

        with col3:
            items_incumplidos = len([d for d in results['demanda'] if d['Cumplimiento'] < 100])
            st.metric("Items Incumplidos", items_incumplidos)

        # Mostrar items con cumplimiento < 100%
        if items_incumplidos > 0:
            st.warning(f"⚠️ Hay {items_incumplidos} items con cumplimiento < 100%")

            df_incumplidos = pd.DataFrame([
                d for d in results['demanda'] if d['Cumplimiento'] < 100
            ])

            st.dataframe(df_incumplidos, use_container_width=True, hide_index=True)

    else:
        st.info("No hay datos de demanda disponibles")

# ==================== TAB 4: SETUP ====================
with tab4:
    st.subheader("Análisis de Tiempos de Setup")

    if results['setups']:
        df_setups = pd.DataFrame(results['setups'])

        # Mostrar tabla
        st.dataframe(df_setups, use_container_width=True, hide_index=True)

        # Descargar CSV
        csv_setups = df_setups.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Descargar Setup (CSV)",
            data=csv_setups,
            file_name="tiempos_setup.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Estadísticas
        st.markdown("---")
        st.subheader("📊 Estadísticas de Setup")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Setup", f"{df_setups['TiempoSetup'].sum():.2f} h")

        with col2:
            st.metric("Setup Promedio", f"{df_setups['TiempoSetup'].mean():.2f} h")

        with col3:
            st.metric("Setup Máximo", f"{df_setups['TiempoSetup'].max():.2f} h")

        with col4:
            st.metric("Cambios Totales", len(df_setups))

        # Por máquina
        st.markdown("---")
        st.markdown("#### Setup por Máquina")

        stats_setup_maquina = df_setups.groupby('Maquina').agg({
            'TiempoSetup': ['sum', 'mean', 'count']
        }).reset_index()
        stats_setup_maquina.columns = ['Maquina', 'Total', 'Promedio', 'Cambios']

        st.dataframe(stats_setup_maquina, use_container_width=True, hide_index=True)

    else:
        st.info("No hay datos de setup disponibles (todos los setups fueron 0)")

# ==================== SIDEBAR: SELECTOR DE SOLUCIONES ====================
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Soluciones Disponibles")

    if st.session_state.get('soluciones'):
        num_soluciones = len(st.session_state.soluciones)

        if num_soluciones > 1:
            st.info(f"Hay {num_soluciones} soluciones guardadas")

            # Selector de solución
            solucion_idx = st.selectbox(
                "Ver solución:",
                range(num_soluciones),
                format_func=lambda x: f"Solución {x + 1} - {st.session_state.soluciones[x].get('timestamp', 'N/A')}"
            )

            if st.button("👁️ Ver Esta Solución", use_container_width=True):
                st.session_state.ultima_solucion = st.session_state.soluciones[solucion_idx]
                st.rerun()
        else:
            st.success(f"Mostrando la única solución disponible")

        # Info de la solución actual
        st.markdown("---")
        st.markdown("**Solución Actual:**")
        st.text(f"Fecha: {results.get('timestamp', 'N/A')}")
        st.text(f"Objetivo: {results['objetivo']} h")
    else:
        st.info("No hay soluciones guardadas")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💡 Exporta los resultados en la página de Exportar</p>
</div>
""", unsafe_allow_html=True)
