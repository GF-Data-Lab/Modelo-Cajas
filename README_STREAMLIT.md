# 📦 Sistema de Optimización de Producción de Cajas - Streamlit

Aplicación web interactiva para optimizar la asignación de producción de cajas en máquinas usando programación lineal entera mixta (MILP) con IBM CPLEX Docplex.

## 🎯 Características

- **📊 Configuración Interactiva**: Carga y edita parámetros del modelo (Excel o CSV)
- **🔧 Optimización**: Ejecuta el modelo CPLEX con configuración personalizable
- **📈 Visualizaciones**: Gráficos interactivos (Gantt, heatmaps, barras, líneas de tiempo)
- **📥 Exportación**: Descarga resultados en Excel, CSV, JSON o TXT

## 📁 Estructura del Proyecto

```
Modelo-Cajas/
├── app.py                          # Aplicación principal
├── pages/                          # Páginas de la aplicación
│   ├── 01_📊_Configuración.py      # Carga y edición de parámetros
│   ├── 02_🔧_Optimización.py       # Ejecución del modelo
│   ├── 03_📈_Resultados.py         # Visualización de resultados
│   └── 04_📥_Exportar.py           # Exportación de datos
├── components/                     # Componentes auxiliares
│   ├── data_loader.py              # Carga de archivos
│   ├── model_runner.py             # Wrapper del modelo CPLEX
│   ├── visualizations.py           # Gráficos con Plotly
│   └── validators.py               # Validación de datos
├── scripts/
│   └── model.py                    # Modelo de optimización CPLEX
├── inputs/                         # Datos de entrada
│   ├── Parametros.xlsx
│   └── csv/                        # CSVs generados
├── outputs/                        # Resultados generados
├── .streamlit/
│   └── config.toml                 # Configuración de tema
├── requirements.txt                # Dependencias Python
└── README_STREAMLIT.md             # Este archivo
```

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- streamlit>=1.28.0
- pandas>=2.0.0
- plotly>=5.17.0
- openpyxl>=3.1.0
- docplex>=2.25.0
- numpy>=1.24.0

### 2. Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### 3. Flujo de Uso

#### Paso 1: Configuración (📊)
1. Ve a la página **"📊 Configuración"**
2. Opciones de carga:
   - **Desde CSVs existentes**: Click en "📂 Cargar desde inputs/csv/"
   - **Subir nuevos archivos**: Sube Excel o múltiples CSVs
3. Edita los datos directamente en la interfaz si es necesario
4. Valida los datos en la pestaña "✅ Validar"

**Archivos necesarios:**
- Turnos.csv
- Disponibilidad_Maquinas.csv
- Productividad_Maquina_Caja.csv
- Tiempo_de_Setup_por_maquina.csv
- Duracion_Turno.csv

#### Paso 2: Optimización (🔧)
1. Ve a la página **"🔧 Optimización"**
2. Configura la demanda por tipo de caja y día
3. Ajusta parámetros del solver:
   - Tiempo límite (segundos)
   - MIP Gap (%)
   - Duración de turno (horas)
4. Click en **"▶️ EJECUTAR MODELO"**
5. Espera a que termine la optimización

#### Paso 3: Resultados (📈)
1. Ve a la página **"📈 Resultados"**
2. Explora:
   - **KPIs**: Métricas principales
   - **Visualizaciones**: Gráficos interactivos
   - **Asignaciones**: Tabla detallada con filtros
   - **Cumplimiento Demanda**: Análisis de cumplimiento
   - **Setup**: Tiempos de cambio

#### Paso 4: Exportar (📥)
1. Ve a la página **"📥 Exportar"**
2. Selecciona qué datos exportar
3. Elige formato:
   - **Excel**: Múltiples hojas en un archivo
   - **CSV (ZIP)**: Archivos CSV comprimidos
   - **JSON**: Formato estructurado
   - **TXT**: Resumen ejecutivo

## 🎨 Diseño y Tema

El tema está configurado en `.streamlit/config.toml`:

- **Color Primario**: Azul corporativo (#0066CC)
- **Fondo**: Blanco (#FFFFFF)
- **Fondo Secundario**: Gris claro (#F0F2F6)
- **Texto**: Oscuro (#262730)

## 📊 Modelo de Optimización

### Objetivo
Minimizar el tiempo total de setup entre cambios de tipos de caja.

### Variables de Decisión
- `x[m,b,d,t,s]`: Asignación binaria (máquina, tipo caja, día, turno, segmento)
- `y[m,b,d,t,s]`: Horas de producción continuas
- `T[m,d,t]`: Tiempo de setup por turno

### Restricciones Principales
1. Satisfacer demanda de cada tipo de caja por día
2. Respetar disponibilidad de máquinas
3. Limitar tiempo de trabajo por turno
4. Máximo un tipo de caja por segmento
5. Asignar segmentos en orden
6. Calcular setup exacto con variables auxiliares

## 🔧 Configuración Avanzada

### Parámetros del Solver (en página de Optimización)

- **Time Limit**: Tiempo máximo de ejecución (10-600s)
- **MIP Gap**: Gap de optimalidad aceptable (0-10%)
- **Duración Turno**: Horas por turno (1-24h)
- **Enforce Tipo**: Forzar compatibilidad máquina-caja
- **Restrict W**: Reducir variables de setup

### Session State

La aplicación usa `st.session_state` para mantener:
- `parametros`: Parámetros extraídos del modelo
- `dataframes`: DataFrames cargados
- `soluciones`: Lista de soluciones guardadas
- `ultima_solucion`: Última solución ejecutada
- `datos_cargados`: Flag de datos disponibles

## 📝 Formato de Datos de Entrada

### Turnos.csv
```csv
DIA,CANTIDAD DE TURNOS
1,2
2,2
```

### Disponibilidad_Maquinas.csv
```csv
Maquina,Dia,Disponibilidad
M1,1,1
M1,2,1
```

### Productividad_Maquina_Caja.csv
```csv
MAQUINA,TIPO_CAJA,PRODUCTIVIDAD
M1,CAJA_A,100
M1,CAJA_B,80
```

### Tiempo_de_Setup_por_maquina.csv
```csv
MAQUINA,TIPO_CAJA_ACTUAL,TIPO_CAJA_A_CAMBIAR,SETUP
M1,CAJA_A,CAJA_B,0.5
M1,CAJA_B,CAJA_A,0.5
```

### Duracion_Turno.csv
```csv
DIA,TURNO,HORAS
1,1,8
1,2,8
```

## 🐛 Solución de Problemas

### El modelo no encuentra solución
- Reduce la demanda
- Aumenta disponibilidad de máquinas
- Aumenta el time limit
- Revisa compatibilidad máquina-caja

### Error al cargar datos
- Verifica que los archivos tengan las columnas correctas
- Asegúrate de que los nombres de máquinas y tipos de caja sean consistentes
- Revisa que no haya valores nulos en columnas clave

### La aplicación es lenta
- Reduce el número de días o máquinas
- Ajusta el time limit del solver
- Aumenta el MIP gap para soluciones más rápidas

## 📧 Soporte

Para reportar problemas o sugerir mejoras, contacta al equipo de desarrollo.

## 📄 Licencia

Uso interno. Todos los derechos reservados.

---

**Powered by:**
- Streamlit
- IBM CPLEX Docplex
- Plotly
- Pandas
