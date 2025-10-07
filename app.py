import streamlit as st

st.set_page_config(
    page_title="Optimización de Cajas",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'inicializado' not in st.session_state:
    st.session_state.inicializado = True
    st.session_state.parametros = {}
    st.session_state.soluciones = []
    st.session_state.modelo_cargado = False
    st.session_state.ultima_ejecucion = None
    st.session_state.datos_cargados = False

# Sidebar
with st.sidebar:
    st.title("📦 Modelo de Cajas")
    st.markdown("---")

    # Estado del sistema
    st.subheader("Estado del Sistema")

    if st.session_state.datos_cargados:
        st.success("✅ Parámetros cargados")
        if st.session_state.parametros:
            st.metric("Máquinas", len(st.session_state.parametros.get('M', [])))
            st.metric("Días", len(st.session_state.parametros.get('D', [])))
            st.metric("Tipos de Caja", len(st.session_state.parametros.get('B', [])))
    else:
        st.info("📋 Carga parámetros en la página de Configuración")

    st.markdown("---")

    if st.session_state.ultima_ejecucion:
        st.success(f"🎯 Última optimización: {st.session_state.ultima_ejecucion}")
        st.metric("Soluciones", len(st.session_state.soluciones))

    st.markdown("---")

    # Botón de reset
    if st.button("🔄 Reiniciar Sesión", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main page
st.title("📦 Sistema de Optimización de Producción de Cajas")

st.markdown("""
### Bienvenido al Sistema de Optimización

Este sistema te permite gestionar y optimizar la asignación de producción de cajas en máquinas,
considerando múltiples factores:

- 🏭 **Disponibilidad de máquinas** por día
- 🔄 **Tiempos de setup** entre tipos de caja
- 📊 **Productividad** de cada máquina por tipo de caja
- ⏰ **Turnos y segmentos** de trabajo
- 📈 **Demanda** por tipo de caja y día
""")

st.markdown("---")

# Métricas generales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Máquinas",
        len(st.session_state.parametros.get('M', [])),
        help="Número de máquinas disponibles en el sistema"
    )

with col2:
    st.metric(
        "Días",
        len(st.session_state.parametros.get('D', [])),
        help="Días de planificación configurados"
    )

with col3:
    st.metric(
        "Tipos de Caja",
        len(st.session_state.parametros.get('B', [])),
        help="Diferentes tipos de cajas a producir"
    )

with col4:
    st.metric(
        "Optimizaciones",
        len(st.session_state.soluciones),
        help="Número de ejecuciones exitosas del modelo"
    )

st.markdown("---")

# Guía de uso
with st.expander("📖 Guía de Uso", expanded=False):
    st.markdown("""
    ### Cómo usar el sistema:

    1. **📊 Configuración**: Carga y edita los parámetros del modelo
        - Sube archivos CSV o Excel con los datos
        - Edita directamente en la interfaz
        - Valida que todos los datos sean correctos

    2. **🔧 Optimización**: Ejecuta el modelo de optimización
        - Define la demanda de cajas por día
        - Configura parámetros del solver
        - Ejecuta y monitorea el progreso

    3. **📈 Resultados**: Visualiza y analiza los resultados
        - Revisa métricas clave (KPIs)
        - Explora gráficos interactivos
        - Filtra por máquina, día o turno

    4. **📥 Exportar**: Descarga los resultados
        - Excel con múltiples hojas
        - CSV comprimido
        - Reportes en PDF

    ---

    **Nota**: Navega usando el menú lateral para acceder a cada sección.
    """)

# Información del modelo
with st.expander("🧮 Sobre el Modelo de Optimización", expanded=False):
    st.markdown("""
    ### Modelo Matemático

    El sistema utiliza un **modelo de programación lineal entera mixta (MILP)** implementado con IBM CPLEX Docplex.

    **Objetivo**: Minimizar el tiempo total de setup entre cambios de tipos de caja.

    **Restricciones principales**:
    - ✓ Satisfacer la demanda de cada tipo de caja por día
    - ✓ Respetar la disponibilidad de máquinas
    - ✓ Limitar el tiempo de trabajo por turno
    - ✓ Considerar compatibilidad máquina-tipo de caja
    - ✓ Gestionar cambios de tipo de caja (setup)

    **Variables de decisión**:
    - `x`: Asignación binaria (máquina-caja-día-turno-segmento)
    - `y`: Horas de producción continuas
    - `T`: Tiempo de setup por turno
    """)

# Mensajes informativos
if not st.session_state.datos_cargados:
    st.info("👈 Comienza por la página **📊 Configuración** en el menú lateral para cargar los parámetros del modelo.")
elif not st.session_state.soluciones:
    st.info("👈 Los parámetros están cargados. Ve a **🔧 Optimización** para ejecutar el modelo.")
else:
    st.success("✅ Sistema listo. Explora los **📈 Resultados** o ejecuta una nueva optimización.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Sistema de Optimización de Producción de Cajas v1.0</p>
    <p>Powered by IBM CPLEX Docplex + Streamlit</p>
</div>
""", unsafe_allow_html=True)
