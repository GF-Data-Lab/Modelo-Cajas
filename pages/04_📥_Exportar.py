import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import io
import zipfile

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Exportar - Modelo Cajas",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Exportar Resultados")
st.markdown("Descarga los resultados de la optimización en diferentes formatos")

# Verificar que haya resultados
if not st.session_state.get('ultima_solucion'):
    st.warning("⚠️ No hay resultados disponibles. Ejecuta el modelo en la página de **Optimización** primero.")
    st.stop()

results = st.session_state.ultima_solucion

# ==================== OPCIONES DE EXPORTACIÓN ====================
st.header("📋 Selecciona qué Exportar")

col1, col2 = st.columns(2)

with col1:
    export_asignaciones = st.checkbox("✅ Asignaciones", value=True)
    export_demanda = st.checkbox("✅ Cumplimiento de Demanda", value=True)
    export_setup = st.checkbox("✅ Tiempos de Setup", value=True)

with col2:
    export_utilizacion = st.checkbox("✅ Utilización de Máquinas", value=True)
    export_kpis = st.checkbox("✅ KPIs y Resumen", value=True)
    export_parametros = st.checkbox("✅ Parámetros del Modelo", value=False)

st.markdown("---")

# ==================== FORMATOS DE EXPORTACIÓN ====================
st.header("📦 Formatos Disponibles")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Excel", "📁 CSV (ZIP)", "📄 JSON", "📋 Resumen de Texto"])

# ==================== TAB 1: EXCEL ====================
with tab1:
    st.subheader("Exportar a Excel (múltiples hojas)")

    st.info("""
    📊 El archivo Excel incluirá una hoja por cada tipo de dato seleccionado:
    - Asignaciones
    - Cumplimiento de Demanda
    - Tiempos de Setup
    - Utilización de Máquinas
    - KPIs (resumen)
    """)

    if st.button("📥 Generar Excel", type="primary", use_container_width=True):
        # Crear archivo Excel en memoria
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja de KPIs
            if export_kpis:
                kpis_data = {
                    'Métrica': [
                        'Objetivo (Minimizar Setup)',
                        'Total Horas Producción',
                        'Total Horas Setup',
                        'Eficiencia (%)',
                        'Total Asignaciones',
                        'Total Cambios Setup',
                        'Timestamp'
                    ],
                    'Valor': [
                        f"{results['objetivo']} h",
                        f"{results['total_produccion_h']} h",
                        f"{results['total_setup_h']} h",
                        f"{(results['total_produccion_h'] / (results['total_produccion_h'] + results['total_setup_h']) * 100):.1f}%",
                        len(results['asignaciones']),
                        len(results['setups']),
                        results.get('timestamp', 'N/A')
                    ]
                }
                df_kpis = pd.DataFrame(kpis_data)
                df_kpis.to_excel(writer, sheet_name='KPIs', index=False)

            # Hoja de Asignaciones
            if export_asignaciones and results['asignaciones']:
                df_asig = pd.DataFrame(results['asignaciones'])
                df_asig.to_excel(writer, sheet_name='Asignaciones', index=False)

            # Hoja de Demanda
            if export_demanda and results['demanda']:
                df_dem = pd.DataFrame(results['demanda'])
                df_dem.to_excel(writer, sheet_name='Cumplimiento_Demanda', index=False)

            # Hoja de Setup
            if export_setup and results['setups']:
                df_setup = pd.DataFrame(results['setups'])
                df_setup.to_excel(writer, sheet_name='Setup', index=False)

            # Hoja de Utilización
            if export_utilizacion and results['utilizacion']:
                df_util = pd.DataFrame(results['utilizacion'])
                df_util.to_excel(writer, sheet_name='Utilizacion', index=False)

            # Hoja de Parámetros
            if export_parametros:
                params = results.get('parametros', {})
                params_data = {
                    'Parámetro': [
                        'Máquinas',
                        'Tipos de Caja',
                        'Días',
                        'Total Turnos'
                    ],
                    'Valor': [
                        ', '.join(params.get('M', [])),
                        ', '.join(params.get('B', [])),
                        ', '.join(map(str, params.get('D', []))),
                        sum(len(v) for v in params.get('T_turnos', {}).values())
                    ]
                }
                df_params = pd.DataFrame(params_data)
                df_params.to_excel(writer, sheet_name='Parametros', index=False)

        # Preparar descarga
        excel_data = output.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="💾 Descargar Excel",
            data=excel_data,
            file_name=f"resultados_optimizacion_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.success("✅ Archivo Excel generado correctamente")

# ==================== TAB 2: CSV ZIP ====================
with tab2:
    st.subheader("Exportar CSVs (archivo ZIP)")

    st.info("""
    📁 Se generará un archivo ZIP con múltiples archivos CSV:
    - asignaciones.csv
    - cumplimiento_demanda.csv
    - tiempos_setup.csv
    - utilizacion_maquinas.csv
    - kpis.csv
    """)

    if st.button("📥 Generar ZIP", type="primary", use_container_width=True):
        # Crear archivo ZIP en memoria
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # KPIs
            if export_kpis:
                kpis_data = {
                    'Métrica': [
                        'Objetivo',
                        'Total_Produccion',
                        'Total_Setup',
                        'Eficiencia',
                        'Asignaciones',
                        'Cambios_Setup'
                    ],
                    'Valor': [
                        results['objetivo'],
                        results['total_produccion_h'],
                        results['total_setup_h'],
                        (results['total_produccion_h'] / (results['total_produccion_h'] + results['total_setup_h']) * 100),
                        len(results['asignaciones']),
                        len(results['setups'])
                    ]
                }
                df_kpis = pd.DataFrame(kpis_data)
                zip_file.writestr('kpis.csv', df_kpis.to_csv(index=False))

            # Asignaciones
            if export_asignaciones and results['asignaciones']:
                df_asig = pd.DataFrame(results['asignaciones'])
                zip_file.writestr('asignaciones.csv', df_asig.to_csv(index=False))

            # Demanda
            if export_demanda and results['demanda']:
                df_dem = pd.DataFrame(results['demanda'])
                zip_file.writestr('cumplimiento_demanda.csv', df_dem.to_csv(index=False))

            # Setup
            if export_setup and results['setups']:
                df_setup = pd.DataFrame(results['setups'])
                zip_file.writestr('tiempos_setup.csv', df_setup.to_csv(index=False))

            # Utilización
            if export_utilizacion and results['utilizacion']:
                df_util = pd.DataFrame(results['utilizacion'])
                zip_file.writestr('utilizacion_maquinas.csv', df_util.to_csv(index=False))

        # Preparar descarga
        zip_data = zip_buffer.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="💾 Descargar ZIP",
            data=zip_data,
            file_name=f"resultados_optimizacion_{timestamp}.zip",
            mime="application/zip",
            use_container_width=True
        )

        st.success("✅ Archivo ZIP generado correctamente")

# ==================== TAB 3: JSON ====================
with tab3:
    st.subheader("Exportar a JSON")

    st.info("""
    📄 El archivo JSON incluirá toda la solución en formato estructurado,
    ideal para procesamiento posterior o integración con otros sistemas.
    """)

    if st.button("📥 Generar JSON", type="primary", use_container_width=True):
        # Preparar datos para JSON
        export_data = {}

        if export_kpis:
            export_data['kpis'] = {
                'objetivo': results['objetivo'],
                'total_produccion_h': results['total_produccion_h'],
                'total_setup_h': results['total_setup_h'],
                'eficiencia': (results['total_produccion_h'] / (results['total_produccion_h'] + results['total_setup_h']) * 100),
                'timestamp': results.get('timestamp', 'N/A')
            }

        if export_asignaciones:
            export_data['asignaciones'] = results['asignaciones']

        if export_demanda:
            export_data['cumplimiento_demanda'] = results['demanda']

        if export_setup:
            export_data['setup'] = results['setups']

        if export_utilizacion:
            export_data['utilizacion'] = results['utilizacion']

        if export_parametros:
            export_data['parametros'] = {
                'M': results.get('parametros', {}).get('M', []),
                'B': results.get('parametros', {}).get('B', []),
                'D': results.get('parametros', {}).get('D', [])
            }

        # Convertir a JSON
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="💾 Descargar JSON",
            data=json_str,
            file_name=f"resultados_optimizacion_{timestamp}.json",
            mime="application/json",
            use_container_width=True
        )

        st.success("✅ Archivo JSON generado correctamente")

        # Previsualización
        with st.expander("👁️ Previsualizar JSON"):
            st.code(json_str, language='json')

# ==================== TAB 4: RESUMEN TEXTO ====================
with tab4:
    st.subheader("Resumen en Texto")

    st.info("""
    📋 Genera un resumen ejecutivo en formato de texto plano
    para copiar o compartir rápidamente.
    """)

    # Generar resumen
    resumen = f"""
================================================================================
               RESUMEN DE OPTIMIZACIÓN - MODELO DE CAJAS
================================================================================

Fecha de Ejecución: {results.get('timestamp', 'N/A')}

--------------------------------------------------------------------------------
OBJETIVO Y MÉTRICAS PRINCIPALES
--------------------------------------------------------------------------------

• Función Objetivo (Minimizar Setup):     {results['objetivo']:.2f} horas
• Total Horas de Producción:              {results['total_produccion_h']:.2f} horas
• Total Horas de Setup:                   {results['total_setup_h']:.2f} horas
• Eficiencia Productiva:                  {(results['total_produccion_h'] / (results['total_produccion_h'] + results['total_setup_h']) * 100):.1f}%

--------------------------------------------------------------------------------
ASIGNACIONES
--------------------------------------------------------------------------------

• Total de Asignaciones Activas:          {len(results['asignaciones'])}
• Total de Cambios de Setup:              {len(results['setups'])}

--------------------------------------------------------------------------------
CUMPLIMIENTO DE DEMANDA
--------------------------------------------------------------------------------

"""

    # Agregar info de demanda
    if results['demanda']:
        df_demanda = pd.DataFrame(results['demanda'])
        cumplimiento_promedio = df_demanda['Cumplimiento'].mean()
        items_100 = len(df_demanda[df_demanda['Cumplimiento'] >= 100])

        resumen += f"""• Cumplimiento Promedio:                  {cumplimiento_promedio:.1f}%
• Items con Cumplimiento 100%:            {items_100}/{len(df_demanda)}
• Total Demandado:                        {df_demanda['Demanda'].sum():.0f}
• Total Producido:                        {df_demanda['Producido'].sum():.0f}

"""

    # Agregar info de máquinas
    if results['utilizacion']:
        df_util = pd.DataFrame(results['utilizacion'])

        resumen += f"""--------------------------------------------------------------------------------
UTILIZACIÓN DE RECURSOS
--------------------------------------------------------------------------------

• Total Máquinas Utilizadas:              {df_util['Maquina'].nunique()}
• Total Días de Planificación:            {df_util['Dia'].nunique()}

"""

    resumen += """================================================================================
                            FIN DEL RESUMEN
================================================================================
"""

    # Mostrar resumen
    st.text_area("📋 Resumen", resumen, height=400)

    # Botón de descarga
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    st.download_button(
        label="💾 Descargar Resumen (.txt)",
        data=resumen,
        file_name=f"resumen_optimizacion_{timestamp}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ==================== EXPORTACIÓN RÁPIDA ====================
st.markdown("---")
st.header("⚡ Exportación Rápida")

st.markdown("Descarga todo en un solo clic:")

col1, col2, col3 = st.columns(3)

with col1:
    # Excel completo
    if st.button("📊 Excel Completo", use_container_width=True):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Todas las hojas
            pd.DataFrame([{
                'Objetivo': results['objetivo'],
                'Produccion': results['total_produccion_h'],
                'Setup': results['total_setup_h']
            }]).to_excel(writer, sheet_name='KPIs', index=False)

            if results['asignaciones']:
                pd.DataFrame(results['asignaciones']).to_excel(writer, sheet_name='Asignaciones', index=False)
            if results['demanda']:
                pd.DataFrame(results['demanda']).to_excel(writer, sheet_name='Demanda', index=False)
            if results['setups']:
                pd.DataFrame(results['setups']).to_excel(writer, sheet_name='Setup', index=False)
            if results['utilizacion']:
                pd.DataFrame(results['utilizacion']).to_excel(writer, sheet_name='Utilizacion', index=False)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "💾 Descargar",
            data=output.getvalue(),
            file_name=f"resultados_completo_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with col2:
    # JSON completo
    if st.button("📄 JSON Completo", use_container_width=True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "💾 Descargar",
            data=json.dumps(results, indent=2, ensure_ascii=False),
            file_name=f"resultados_completo_{timestamp}.json",
            mime="application/json",
            use_container_width=True
        )

with col3:
    # Resumen TXT
    if st.button("📋 Resumen TXT", use_container_width=True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "💾 Descargar",
            data=resumen,
            file_name=f"resumen_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>💡 Los archivos se generan en tiempo real sin guardarse en el servidor</p>
</div>
""", unsafe_allow_html=True)
