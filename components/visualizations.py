import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Dict, List

class Visualizations:
    """Clase para crear visualizaciones de los resultados"""

    @staticmethod
    def create_gantt_chart(asignaciones: List[Dict]) -> go.Figure:
        """Crea un diagrama de Gantt de las asignaciones"""
        if not asignaciones:
            return None

        df = pd.DataFrame(asignaciones)

        # Crear identificador único para cada asignación
        df['Task'] = df['Maquina'] + ' - Día ' + df['Dia'].astype(str)
        df['Start'] = (df['Dia'] - 1) * 24 + (df['Turno'] - 1) * 8 + (df['Segmento'] - 1) * 4
        df['Finish'] = df['Start'] + df['Horas']

        fig = px.timeline(
            df,
            x_start='Start',
            x_end='Finish',
            y='Task',
            color='TipoCaja',
            title='Diagrama de Gantt - Asignaciones de Producción',
            labels={'Task': 'Máquina-Día', 'TipoCaja': 'Tipo de Caja'},
            hover_data=['Turno', 'Segmento', 'Horas', 'Cajas']
        )

        fig.update_layout(
            height=600,
            xaxis_title="Tiempo (horas)",
            yaxis_title="Máquina - Día",
            showlegend=True
        )

        return fig

    @staticmethod
    def create_utilization_heatmap(utilizacion: List[Dict]) -> go.Figure:
        """Crea un heatmap de utilización de máquinas"""
        if not utilizacion:
            return None

        df = pd.DataFrame(utilizacion)

        # Pivotar para crear matriz
        pivot = df.pivot(index='Maquina', columns='Dia', values='HorasTotal')

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f'Día {d}' for d in pivot.columns],
            y=pivot.index,
            colorscale='Blues',
            text=pivot.values,
            texttemplate='%{text:.1f}h',
            textfont={"size": 10},
            colorbar=dict(title="Horas")
        ))

        fig.update_layout(
            title='Utilización de Máquinas por Día (Horas Totales)',
            xaxis_title='Día',
            yaxis_title='Máquina',
            height=400
        )

        return fig

    @staticmethod
    def create_setup_bar_chart(setups: List[Dict]) -> go.Figure:
        """Crea un gráfico de barras de tiempos de setup por máquina"""
        if not setups:
            return None

        df = pd.DataFrame(setups)

        # Agrupar por máquina
        df_grouped = df.groupby('Maquina')['TiempoSetup'].sum().reset_index()
        df_grouped = df_grouped.sort_values('TiempoSetup', ascending=False)

        fig = go.Figure(data=[
            go.Bar(
                x=df_grouped['Maquina'],
                y=df_grouped['TiempoSetup'],
                text=df_grouped['TiempoSetup'].round(2),
                textposition='auto',
                marker_color='indianred'
            )
        ])

        fig.update_layout(
            title='Tiempo Total de Setup por Máquina',
            xaxis_title='Máquina',
            yaxis_title='Tiempo de Setup (horas)',
            height=400
        )

        return fig

    @staticmethod
    def create_demand_fulfillment_chart(demanda: List[Dict]) -> go.Figure:
        """Crea un gráfico de cumplimiento de demanda"""
        if not demanda:
            return None

        df = pd.DataFrame(demanda)

        # Agrupar por tipo de caja
        df_grouped = df.groupby('TipoCaja').agg({
            'Demanda': 'sum',
            'Producido': 'sum'
        }).reset_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Demanda',
            x=df_grouped['TipoCaja'],
            y=df_grouped['Demanda'],
            marker_color='lightblue'
        ))

        fig.add_trace(go.Bar(
            name='Producido',
            x=df_grouped['TipoCaja'],
            y=df_grouped['Producido'],
            marker_color='darkblue'
        ))

        fig.update_layout(
            title='Demanda vs Producción por Tipo de Caja',
            xaxis_title='Tipo de Caja',
            yaxis_title='Cantidad',
            barmode='group',
            height=400
        )

        return fig

    @staticmethod
    def create_production_timeline(asignaciones: List[Dict]) -> go.Figure:
        """Crea una línea de tiempo de producción por tipo de caja"""
        if not asignaciones:
            return None

        df = pd.DataFrame(asignaciones)

        # Agrupar por tipo de caja y día
        df_grouped = df.groupby(['TipoCaja', 'Dia'])['Cajas'].sum().reset_index()

        fig = px.line(
            df_grouped,
            x='Dia',
            y='Cajas',
            color='TipoCaja',
            title='Producción por Tipo de Caja a lo Largo de los Días',
            markers=True
        )

        fig.update_layout(
            xaxis_title='Día',
            yaxis_title='Cajas Producidas',
            height=400
        )

        return fig

    @staticmethod
    def create_machine_productivity_pie(utilizacion: List[Dict]) -> go.Figure:
        """Crea un gráfico de pie de horas productivas vs setup"""
        if not utilizacion:
            return None

        df = pd.DataFrame(utilizacion)

        total_prod = df['HorasProduccion'].sum()
        total_setup = df['HorasSetup'].sum()

        fig = go.Figure(data=[go.Pie(
            labels=['Producción', 'Setup'],
            values=[total_prod, total_setup],
            hole=.3,
            marker_colors=['#2ecc71', '#e74c3c']
        )])

        fig.update_layout(
            title='Distribución de Tiempo: Producción vs Setup',
            height=400
        )

        return fig

    @staticmethod
    def display_kpis(results: Dict):
        """Muestra KPIs principales en tarjetas"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Objetivo (Setup Total)",
                f"{results['objetivo']} h",
                help="Tiempo total de setup minimizado"
            )

        with col2:
            st.metric(
                "Horas de Producción",
                f"{results['total_produccion_h']} h",
                help="Suma de horas productivas en todas las máquinas"
            )

        with col3:
            eficiencia = (results['total_produccion_h'] /
                         (results['total_produccion_h'] + results['total_setup_h']) * 100)
            st.metric(
                "Eficiencia",
                f"{eficiencia:.1f}%",
                help="% de tiempo productivo vs tiempo total"
            )

        with col4:
            # Calcular cumplimiento promedio
            demanda_df = pd.DataFrame(results['demanda'])
            cumplimiento_promedio = demanda_df['Cumplimiento'].mean()
            st.metric(
                "Cumplimiento Promedio",
                f"{cumplimiento_promedio:.1f}%",
                help="% promedio de cumplimiento de demanda"
            )

    @staticmethod
    def display_asignaciones_table(asignaciones: List[Dict]):
        """Muestra tabla de asignaciones con filtros"""
        if not asignaciones:
            st.warning("No hay asignaciones para mostrar")
            return

        df = pd.DataFrame(asignaciones)

        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            maquinas = ['Todas'] + sorted(df['Maquina'].unique().tolist())
            maquina_filtro = st.selectbox("Filtrar por Máquina", maquinas)

        with col2:
            dias = ['Todos'] + sorted(df['Dia'].unique().tolist())
            dia_filtro = st.selectbox("Filtrar por Día", dias)

        with col3:
            cajas = ['Todas'] + sorted(df['TipoCaja'].unique().tolist())
            caja_filtro = st.selectbox("Filtrar por Tipo de Caja", cajas)

        # Aplicar filtros
        df_filtrado = df.copy()

        if maquina_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Maquina'] == maquina_filtro]

        if dia_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Dia'] == dia_filtro]

        if caja_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['TipoCaja'] == caja_filtro]

        # Mostrar tabla
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True
        )

        # Estadísticas del filtro
        st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df)} asignaciones")

    @staticmethod
    def display_demanda_table(demanda: List[Dict]):
        """Muestra tabla de cumplimiento de demanda"""
        if not demanda:
            st.warning("No hay datos de demanda")
            return

        df = pd.DataFrame(demanda)

        # Colorear según cumplimiento
        def color_cumplimiento(val):
            if val >= 100:
                return 'background-color: #d4edda'  # Verde
            elif val >= 95:
                return 'background-color: #fff3cd'  # Amarillo
            else:
                return 'background-color: #f8d7da'  # Rojo

        styled_df = df.style.applymap(
            color_cumplimiento,
            subset=['Cumplimiento']
        )

        st.dataframe(styled_df, use_container_width=True, hide_index=True)
