# 📦 Sistema de Optimización de Producción de Cajas

> Aplicación web interactiva desarrollada con **Streamlit** para optimizar la asignación de producción de cajas en máquinas usando **Programación Lineal Entera Mixta (MILP)** con **IBM CPLEX Docplex**.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.49-red.svg)](https://streamlit.io/)
[![CPLEX](https://img.shields.io/badge/CPLEX-Docplex%202.30-green.svg)](https://www.ibm.com/products/ilog-cplex-optimization-studio)

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características Principales](#-características-principales)
3. [Arquitectura del Sistema](#-arquitectura-del-sistema)
4. [Instalación](#-instalación)
5. [Uso de la Aplicación](#-uso-de-la-aplicación)
6. [Modelo Matemático](#-modelo-matemático)
7. [Formato de Datos](#-formato-de-datos)
8. [Configuración Avanzada](#-configuración-avanzada)
9. [Solución de Problemas](#-solución-de-problemas)
10. [Desarrollo](#-desarrollo)

---

## 🎯 Descripción General

Este sistema permite planificar y optimizar la producción de diferentes tipos de cajas en múltiples máquinas a lo largo de varios días, considerando:

- **Disponibilidad variable** de máquinas por día
- **Tiempos de setup** entre cambios de tipos de caja
- **Productividad específica** de cada máquina para cada tipo de caja
- **Compatibilidad** máquina-tipo de caja
- **Turnos y segmentos** de trabajo configurables
- **Demanda diaria** por tipo de caja

**Objetivo:** Minimizar el tiempo total de setup entre cambios de producción, maximizando la eficiencia operativa.

---

## ✨ Características Principales

### 🎨 Interfaz de Usuario
- **Dashboard interactivo** con métricas en tiempo real
- **Navegación multipágina** intuitiva
- **Tema personalizable** (configurado en `.streamlit/config.toml`)
- **Visualizaciones interactivas** con Plotly
- **Validación automática** de datos con mensajes descriptivos

### 📊 Funcionalidades

#### 1. Configuración de Parámetros
- ✅ Carga desde archivos CSV o Excel
- ✅ **Descarga de templates** con formato correcto
- ✅ **Validación automática** de formato y estructura
- ✅ Editor de datos en línea con `st.data_editor`
- ✅ Detección de inconsistencias entre archivos

#### 2. Optimización
- ✅ Configuración de demanda interactiva
- ✅ Parámetros del solver ajustables (time limit, MIP gap)
- ✅ Monitoreo de progreso en tiempo real
- ✅ Historial de ejecuciones

#### 3. Resultados
- ✅ **KPIs clave**: Objetivo, eficiencia, cumplimiento
- ✅ **Diagrama de Gantt** de asignaciones
- ✅ **Heatmap** de utilización de máquinas
- ✅ **Gráficos de barras** para tiempos de setup
- ✅ **Análisis de cumplimiento** de demanda
- ✅ Tablas con filtros dinámicos

#### 4. Exportación
- ✅ Excel con múltiples hojas
- ✅ CSV comprimido (ZIP)
- ✅ JSON estructurado
- ✅ Resumen ejecutivo en TXT

---

## 🏗️ Arquitectura del Sistema

```
Modelo-Cajas/
│
├── 📱 FRONTEND (Streamlit)
│   ├── app.py                          # Página principal y dashboard
│   └── pages/                          # Páginas multipágina
│       ├── 01_📊_Configuración.py      # Carga/edición de parámetros
│       ├── 02_🔧_Optimización.py       # Ejecución del modelo
│       ├── 03_📈_Resultados.py         # Visualizaciones
│       └── 04_📥_Exportar.py           # Descarga de resultados
│
├── 🧩 COMPONENTES
│   ├── components/
│   │   ├── data_loader.py              # Carga de CSV/Excel
│   │   ├── validators.py               # Validación de datos y formato
│   │   ├── model_runner.py             # Wrapper del modelo CPLEX
│   │   └── visualizations.py           # Gráficos Plotly
│   │
│   └── scripts/
│       └── model.py                    # Modelo CPLEX (Processing + build_model)
│
├── 📁 DATOS
│   ├── inputs/                         # Datos de entrada
│   │   ├── Parametros.xlsx             # Excel original
│   │   └── csv/                        # CSVs convertidos
│   │       ├── Turnos.csv
│   │       ├── Disponibilidad_Maquinas.csv
│   │       ├── Productividad_Maquina_Caja.csv
│   │       ├── Tiempo_de_Setup_por_maquina.csv
│   │       └── Duracion_Turno.csv
│   │
│   ├── templates/                      # Templates descargables
│   └── outputs/                        # Resultados generados
│
└── ⚙️ CONFIGURACIÓN
    ├── .streamlit/config.toml          # Tema y configuración
    ├── requirements.txt                # Dependencias Python
    └── README.md                       # Esta documentación

```

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.13** o superior
- **pip** (gestor de paquetes Python)
- **IBM CPLEX** (opcional, Docplex puede usar solver gratuito limitado)

### Paso 1: Clonar/Descargar el Proyecto

```bash
cd "C:\Users\bherr\opt cajas\Modelo-Cajas"
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias instaladas:**
```
streamlit>=1.28.0       # Framework web
pandas>=2.0.0           # Manipulación de datos
plotly>=5.17.0          # Gráficos interactivos
openpyxl>=3.1.0         # Lectura/escritura de Excel
docplex>=2.25.0         # IBM CPLEX para optimización
numpy>=1.24.0           # Operaciones numéricas
python-dateutil>=2.8.0  # Manejo de fechas
```

### Paso 3: Verificar Instalación

```bash
streamlit --version
# Debería mostrar: Streamlit, version 1.49.1 (o superior)
```

---

## 💻 Uso de la Aplicación

### Iniciar la Aplicación

```bash
streamlit run app.py
```

**Puertos alternativos:**
```bash
streamlit run app.py --server.port 8508
```

La aplicación se abrirá automáticamente en: `http://localhost:8501` (o el puerto especificado)

### URLs de Acceso

- **Local**: `http://localhost:8501`
- **Red local**: `http://<tu-ip-local>:8501`
- **Externa**: `http://<tu-ip-publica>:8501`

---

## 📖 Guía de Uso Paso a Paso

### 1️⃣ CONFIGURACIÓN (📊)

#### Opción A: Cargar Datos Existentes

1. Ve a la página **"📊 Configuración"** (sidebar izquierdo)
2. Click en **"📂 Cargar desde inputs/csv/"**
3. Los datos se validarán automáticamente
4. Verifica que aparezca: ✅ Datos cargados y validados correctamente

#### Opción B: Subir Nuevos Archivos

1. **Descargar templates** (botones en la sección "📥 Descargar Templates"):
   - 📄 Turnos.csv
   - 📄 Disponibilidad.csv
   - 📄 Productividad.csv
   - 📄 Setup.csv
   - 📄 Duración Turno.csv

2. **Editar templates** con tus datos en Excel/LibreOffice

3. **Subir archivos**:
   - Selecciona "Excel (un archivo)" o "CSV (múltiples archivos)"
   - Upload tus archivos editados
   - La aplicación validará:
     - ✓ Columnas requeridas
     - ✓ Tipos de datos
     - ✓ Rangos válidos
     - ✓ Consistencia entre archivos

4. Si hay errores:
   - ❌ Se mostrarán mensajes específicos
   - 💡 Descarga nuevamente los templates para comparar

5. Click en **"💾 Usar estos datos"**

#### Editar Datos Cargados

1. Ve a la pestaña **"📝 Editar Datos"**
2. Selecciona la tabla a editar
3. Usa el editor interactivo para modificar valores
4. Click en **"💾 Guardar Cambios"**

---

### 2️⃣ OPTIMIZACIÓN (🔧)

1. Ve a la página **"🔧 Optimización"**

2. **Configurar Demanda**:
   - Edita la tabla de demanda por tipo de caja y día
   - Valores predeterminados: 10 cajas
   - Puedes usar **"🔄 Reset Demanda"** para restaurar valores

3. **Parámetros del Solver**:
   - **Tiempo Límite**: 10-600 segundos (default: 60s)
   - **MIP Gap**: 0-10% (default: 1%)
   - **Duración Turno**: 1-24 horas (default: 8h)

4. **Opciones Avanzadas** (expandir):
   - ☑️ Forzar Compatibilidad Máquina-Caja
   - ☑️ Restringir Variables W por Tipo
   - Duración Segmento (default: Turno/2)

5. **Ejecutar**:
   - Click en **"▶️ EJECUTAR MODELO"**
   - Barra de progreso mostrará el avance
   - Log del solver en tiempo real

6. **Resultados**:
   - ✅ Solución encontrada → Resumen de KPIs
   - ❌ Infactible → Sugerencias para ajustar parámetros

7. **Historial**:
   - Todas las ejecuciones se guardan en sesión
   - Tabla con ID, fecha, objetivo, eficiencia
   - **"🗑️ Limpiar Historial"** para borrar

---

### 3️⃣ RESULTADOS (📈)

#### 🎯 KPIs Principales
- **Objetivo (Setup Total)**: Tiempo total de setup minimizado
- **Horas de Producción**: Suma de horas productivas
- **Eficiencia**: % tiempo productivo vs total
- **Cumplimiento Promedio**: % de demanda satisfecha

#### 📊 Visualizaciones (Tab 1)
1. **Diagrama de Gantt**: Timeline de asignaciones por máquina-día
2. **Heatmap**: Utilización de máquinas por día
3. **Setup por Máquina**: Gráfico de barras
4. **Demanda vs Producción**: Comparación por tipo de caja
5. **Distribución de Tiempo**: Pie chart producción/setup
6. **Producción Timeline**: Evolución por día

#### 📋 Asignaciones (Tab 2)
- Tabla completa de asignaciones (Máquina, Tipo Caja, Día, Turno, Segmento, Horas, Cajas)
- **Filtros dinámicos**: Por máquina, día, tipo de caja
- **Descarga CSV**: Botón de exportación
- **Estadísticas agregadas**: Por máquina y por tipo de caja

#### 📦 Cumplimiento Demanda (Tab 3)
- Tabla con colores:
  - 🟢 Verde: ≥ 100% cumplimiento
  - 🟡 Amarillo: 95-99% cumplimiento
  - 🔴 Rojo: < 95% cumplimiento
- **Análisis**:
  - Items con 100% cumplimiento
  - Cumplimiento promedio
  - Items incumplidos (detalle)

#### ⚙️ Setup (Tab 4)
- Tabla de tiempos de setup por turno
- **Estadísticas**: Total, promedio, máximo, cantidad de cambios
- **Por máquina**: Total, promedio, cambios

---

### 4️⃣ EXPORTAR (📥)

#### Seleccionar Qué Exportar
- ✅ Asignaciones
- ✅ Cumplimiento de Demanda
- ✅ Tiempos de Setup
- ✅ Utilización de Máquinas
- ✅ KPIs y Resumen
- ✅ Parámetros del Modelo

#### Formatos Disponibles

##### 📊 Excel
- Múltiples hojas en un solo archivo
- Formato: `resultados_optimizacion_YYYYMMDD_HHMMSS.xlsx`
- Hojas: KPIs, Asignaciones, Cumplimiento_Demanda, Setup, Utilizacion, Parametros

##### 📁 CSV (ZIP)
- Múltiples archivos CSV comprimidos
- Formato: `resultados_optimizacion_YYYYMMDD_HHMMSS.zip`
- Archivos: kpis.csv, asignaciones.csv, cumplimiento_demanda.csv, tiempos_setup.csv, utilizacion_maquinas.csv

##### 📄 JSON
- Formato estructurado para integración con otros sistemas
- Previsualización del JSON antes de descargar
- Formato: `resultados_optimizacion_YYYYMMDD_HHMMSS.json`

##### 📋 TXT
- Resumen ejecutivo en texto plano
- Formato legible para informes rápidos
- Formato: `resumen_optimizacion_YYYYMMDD_HHMMSS.txt`

#### ⚡ Exportación Rápida
- **Excel Completo**: Todo en Excel con un click
- **JSON Completo**: Solución completa en JSON
- **Resumen TXT**: Solo el resumen

---

## 🧮 Modelo Matemático

### Definición del Problema

**Dado:**
- `M`: Conjunto de máquinas
- `B`: Conjunto de tipos de caja
- `D`: Conjunto de días
- `T_turnos`: Turnos por día
- `S_segmentos`: Segmentos por turno (fijo: 2)

**Parámetros:**
- `Disp[m,d]`: Disponibilidad de máquina `m` en día `d` (0/1)
- `Prod[m,b]`: Productividad de máquina `m` para caja `b` (cajas/hora)
- `Tipo[m,b]`: Compatibilidad máquina-caja (0/1)
- `Setup[m,b1,b2]`: Tiempo de setup de `b1` a `b2` en máquina `m` (horas)
- `Dem[b,d]`: Demanda de caja `b` en día `d` (cajas)
- `Tturn`: Duración de turno (horas)

**Variables de Decisión:**
- `x[m,b,d,t,s]`: Binaria. 1 si máquina `m` produce caja `b` en día `d`, turno `t`, segmento `s`
- `y[m,b,d,t,s]`: Continua. Horas de producción en la asignación anterior
- `T[m,d,t]`: Continua. Tiempo de setup en máquina `m`, día `d`, turno `t`
- `w[m,b1,b2,d,t]`: Continua. Variable auxiliar para setup exacto

### Función Objetivo

```
Minimizar: Σ T[m,d,t]  ∀m∈M, d∈D, t∈T_turnos
```

**Objetivo:** Minimizar el tiempo total de setup entre cambios de tipos de caja.

### Restricciones

#### R1: Satisfacer Demanda
```
Σ y[m,b,d,t,s] * Prod[m,b] ≥ Dem[b,d]  ∀b∈B, d∈D
  m,t,s
```

#### R2: Límite de Tiempo por Turno
```
Σ y[m,b,d,t,s] + T[m,d,t] ≤ Tturn * Disp[m,d]  ∀m∈M, d∈D, t∈T_turnos
 b,s
```

#### R3: Vincular Variables Binarias y Continuas
```
y[m,b,d,t,s] ≤ Tseg[s] * x[m,b,d,t,s]  ∀m,b,d,t,s
```

#### R4: Máximo 1 Tipo por Segmento
```
Σ x[m,b,d,t,s] ≤ 1  ∀m∈M, d∈D, t∈T_turnos, s∈S_segmentos
 b
```

#### R5: Asignar Segmentos en Orden
```
Σ x[m,b,d,t,s2] ≤ Σ x[m,b,d,t,s1]  ∀m∈M, d∈D, t∈T_turnos
 b                 b
```

#### R6: Cálculo Exacto de Setup
```
w[m,b1,b2,d,t] ≤ x[m,b1,d,t,s1]
w[m,b1,b2,d,t] ≤ x[m,b2,d,t,s2]
w[m,b1,b2,d,t] ≥ x[m,b1,d,t,s1] + x[m,b2,d,t,s2] - 1

T[m,d,t] ≥ Σ Setup[m,b1,b2] * w[m,b1,b2,d,t]  ∀m,d,t
           b1,b2
```

#### R7: Compatibilidad Máquina-Caja (Opcional)
```
x[m,b,d,t,s] = 0  si Tipo[m,b] = 0
```

### Complejidad

- **Tipo**: MILP (Mixed Integer Linear Programming)
- **Variables**: O(|M| × |B| × |D| × |T| × |S|) binarias + continuas
- **Restricciones**: O(|M| × |B|² × |D| × |T|)
- **Solver**: IBM CPLEX (comercial) o COIN-OR CBC (open source)

---

## 📁 Formato de Datos

### 1. Turnos.csv

**Columnas requeridas:**
- `DIA` (int): Número de día (≥ 1)
- `CANTIDAD DE TURNOS` (int): Cantidad de turnos en ese día (≥ 1)

**Ejemplo:**
```csv
DIA,CANTIDAD DE TURNOS
1,2
2,2
3,2
```

**Validación:**
- DIA > 0
- CANTIDAD DE TURNOS > 0

---

### 2. Disponibilidad_Maquinas.csv

**Columnas requeridas:**
- `Maquina` (string): Identificador de máquina
- `Dia` (int): Número de día (≥ 1)
- `Disponibilidad` (int): 0 (no disponible) o 1 (disponible)

**Ejemplo:**
```csv
Maquina,Dia,Disponibilidad
M1,1,1
M1,2,1
M2,1,0
M2,2,1
```

**Validación:**
- Dia > 0
- Disponibilidad ∈ {0, 1}

---

### 3. Productividad_Maquina_Caja.csv

**Columnas requeridas:**
- `MAQUINA` (string): Identificador de máquina
- `TIPO_CAJA` (string): Identificador de tipo de caja
- `PRODUCTIVIDAD` (float): Cajas por hora (≥ 0)

**Ejemplo:**
```csv
MAQUINA,TIPO_CAJA,PRODUCTIVIDAD
M1,CAJA_A,100
M1,CAJA_B,80
M2,CAJA_A,95
M2,CAJA_B,0
```

**Nota:** Productividad = 0 indica incompatibilidad (máquina no puede producir ese tipo)

**Validación:**
- PRODUCTIVIDAD ≥ 0

---

### 4. Tiempo_de_Setup_por_maquina.csv

**Columnas requeridas:**
- `MAQUINA` (string): Identificador de máquina
- `TIPO_CAJA_ACTUAL` (string): Tipo de caja que se está produciendo
- `TIPO_CAJA_A_CAMBIAR` (string): Tipo de caja a cambiar
- `SETUP` (float): Tiempo de setup en horas (≥ 0)

**Ejemplo:**
```csv
MAQUINA,TIPO_CAJA_ACTUAL,TIPO_CAJA_A_CAMBIAR,SETUP
M1,CAJA_A,CAJA_B,0.5
M1,CAJA_B,CAJA_A,0.5
M2,CAJA_A,CAJA_B,0.4
```

**Nota:** Si `TIPO_CAJA_ACTUAL = TIPO_CAJA_A_CAMBIAR`, el setup debería ser 0 (se agrega automáticamente)

**Validación:**
- SETUP ≥ 0

---

### 5. Duracion_Turno.csv

**Columnas requeridas:**
- `DIA` (int): Número de día (≥ 1)
- `TURNO` (int): Número de turno (≥ 1)
- `HORAS` (float): Duración del turno en horas (0.1 - 24)

**Ejemplo:**
```csv
DIA,TURNO,HORAS
1,1,8
1,2,8
2,1,8
2,2,8
```

**Validación:**
- DIA > 0
- TURNO > 0
- 0.1 ≤ HORAS ≤ 24

---

## ⚙️ Configuración Avanzada

### Tema Visual

Editar `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0066CC"             # Color primario (botones, links)
backgroundColor = "#FFFFFF"          # Fondo principal
secondaryBackgroundColor = "#F0F2F6" # Fondo secundario (sidebar)
textColor = "#262730"                # Color de texto
font = "sans serif"                  # Fuente

[server]
port = 8501                          # Puerto por defecto
headless = true                      # Sin GUI (producción)
```

### Parámetros del Modelo

En `pages/02_🔧_Optimización.py`, puedes ajustar valores predeterminados:

```python
time_limit = st.number_input(
    "Tiempo Límite (segundos)",
    value=60,  # ← Cambiar aquí
    ...
)
```

### Session State

Variables globales en `st.session_state`:

```python
st.session_state.parametros          # Dict con M, B, D, Disp, Prod, etc.
st.session_state.dataframes          # Dict con DataFrames cargados
st.session_state.soluciones          # Lista de soluciones ejecutadas
st.session_state.ultima_solucion     # Última solución (para Resultados)
st.session_state.datos_cargados      # Bool: ¿Hay datos cargados?
st.session_state.modelo_cargado      # Bool: ¿Modelo inicializado?
st.session_state.demanda_config      # DataFrame de demanda
```

---

## 🐛 Solución de Problemas

### 1. El modelo no encuentra solución (Infactible)

**Causas comunes:**
- Demanda muy alta para la capacidad disponible
- Pocas máquinas disponibles
- Muchas incompatibilidades (productividad = 0)
- Turnos muy cortos

**Soluciones:**
1. **Reducir demanda**:
   - En la página de Optimización, edita la tabla de demanda
   - Reduce valores gradualmente (ej: de 100 a 50)

2. **Aumentar disponibilidad**:
   - En Configuración → Editar Datos → Disponibilidad Maquinas
   - Cambia 0 → 1 en más máquinas/días

3. **Aumentar time limit**:
   - En Optimización, sube "Tiempo Límite" a 300-600s
   - Dale más tiempo al solver para explorar

4. **Relajar restricciones**:
   - Opciones Avanzadas → Desmarcar "Forzar Compatibilidad"
   - Aumenta "Duración Turno"

---

### 2. Error al cargar archivos CSV

**Error:** `KeyError: 'DIA'` o columnas faltantes

**Solución:**
1. Descarga los **templates** desde la página de Configuración
2. Compara tu archivo con el template
3. Asegúrate de que:
   - Las columnas tengan los nombres exactos (case-insensitive tolerado)
   - No haya espacios extra en los nombres de columnas
   - El archivo use codificación UTF-8

**Error:** `ValueError: could not convert string to float`

**Solución:**
- Revisa que las columnas numéricas no tengan texto
- Usa punto (.) para decimales, no coma (,)
- Elimina símbolos como $ o %

---

### 3. La aplicación no carga o se cuelga

**Solución:**
1. Cerrar y reiniciar Streamlit:
   ```bash
   # Presiona Ctrl+C en la terminal
   streamlit run app.py
   ```

2. Limpiar caché:
   ```bash
   streamlit cache clear
   ```

3. Verificar que no haya otros procesos en el mismo puerto:
   ```bash
   # Windows
   netstat -ano | findstr :8501
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -i :8501
   kill -9 <PID>
   ```

---

### 4. El solver es muy lento

**Causas:**
- Problema muy grande (muchas máquinas × días × tipos de caja)
- MIP gap muy pequeño (busca solución muy óptima)

**Soluciones:**
1. **Aumentar MIP gap**:
   - En Optimización, sube "MIP Gap" a 5-10%
   - Acepta soluciones "buenas" en vez de "óptimas"

2. **Reducir tamaño del problema**:
   - Menos días (planifica en ventanas cortas)
   - Agrupar tipos de caja similares
   - Menos máquinas (solo las críticas)

3. **Ajustar opciones avanzadas**:
   - Marca "Restringir Variables W por Tipo"
   - Reduce variables auxiliares

---

### 5. Errores de importación de módulos

**Error:** `ModuleNotFoundError: No module named 'docplex'`

**Solución:**
```bash
pip install docplex
# o reinstalar todo
pip install -r requirements.txt --force-reinstall
```

**Error:** Problemas con `pandas` o `streamlit`

**Solución:**
```bash
pip install --upgrade pandas streamlit
```

---

## 👨‍💻 Desarrollo

### Estructura de Código

#### `app.py`
- Página principal con dashboard
- Inicializa `st.session_state`
- Sidebar con estado del sistema

#### `pages/01_📊_Configuración.py`
- Carga de archivos (CSV/Excel)
- Descarga de templates
- Validación de formato y datos
- Editor de datos

#### `pages/02_🔧_Optimización.py`
- Configuración de demanda
- Parámetros del solver
- Ejecución del modelo
- Historial de soluciones

#### `pages/03_📈_Resultados.py`
- KPIs principales
- Visualizaciones interactivas
- Tablas con filtros
- Análisis de cumplimiento

#### `pages/04_📥_Exportar.py`
- Exportación a Excel/CSV/JSON/TXT
- Selección de datos a exportar
- Generación de reportes

#### `components/data_loader.py`
- `DataLoader`: Clase para cargar Excel/CSV
- `load_from_excel()`: Carga desde Excel multi-hoja
- `load_from_csv_folder()`: Carga desde carpeta CSV
- `validate_dataframe()`: Valida estructura
- `upload_files_widget()`: Widget de upload

#### `components/validators.py`
- `DataValidator`: Validación de datos
- `EXPECTED_FORMATS`: Dict con formatos esperados
- `validate_file_format()`: Valida formato de archivo
- `validate_turnos/disponibilidad/productividad/setup/duracion_turno()`: Validadores específicos
- `check_consistency()`: Verifica consistencia entre archivos

#### `components/model_runner.py`
- `ModelRunner`: Wrapper del modelo CPLEX
- `initialize_from_dataframes()`: Inicializa Processing
- `extract_parameters()`: Extrae parámetros del modelo
- `build_and_solve()`: Construye y resuelve el modelo
- `_extract_solution()`: Procesa la solución

#### `components/visualizations.py`
- `Visualizations`: Clase para gráficos Plotly
- `create_gantt_chart()`: Diagrama de Gantt
- `create_utilization_heatmap()`: Heatmap de utilización
- `create_setup_bar_chart()`: Gráfico de barras de setup
- `create_demand_fulfillment_chart()`: Cumplimiento de demanda
- `display_kpis()`: Muestra KPIs en tarjetas

#### `scripts/model.py`
- `Processing`: Clase para procesar datos de entrada
  - `process_turnos()`: Procesa turnos por día
  - `process_disponibilidad_maquinas()`: Procesa disponibilidad
  - `process_tiempo_setup()`: Procesa tiempos de setup
  - `process_turn_duration()`: Procesa duración de turnos
  - `process_productividad_y_tipo()`: Procesa productividad y compatibilidad

- `build_model()`: Construye el modelo CPLEX
  - Crea variables `x`, `y`, `T`, `w`
  - Agrega restricciones R1-R7
  - Define función objetivo

---

### Agregar Nueva Visualización

**Ejemplo:** Agregar gráfico de líneas de eficiencia por día

1. Editar `components/visualizations.py`:

```python
@staticmethod
def create_efficiency_timeline(utilizacion: List[Dict]) -> go.Figure:
    """Crea línea de tiempo de eficiencia por día"""
    df = pd.DataFrame(utilizacion)

    # Calcular eficiencia por día
    df_day = df.groupby('Dia').agg({
        'HorasProduccion': 'sum',
        'HorasSetup': 'sum'
    }).reset_index()

    df_day['Eficiencia'] = (df_day['HorasProduccion'] /
                            (df_day['HorasProduccion'] + df_day['HorasSetup']) * 100)

    fig = px.line(
        df_day,
        x='Dia',
        y='Eficiencia',
        title='Eficiencia por Día (%)',
        markers=True
    )

    return fig
```

2. Usar en `pages/03_📈_Resultados.py`:

```python
# En la sección de visualizaciones
st.markdown("### 📈 Eficiencia por Día")
efficiency_chart = Visualizations.create_efficiency_timeline(results['utilizacion'])
if efficiency_chart:
    st.plotly_chart(efficiency_chart, use_container_width=True)
```

---

### Agregar Nueva Restricción al Modelo

**Ejemplo:** Limitar máximo 3 cambios de setup por máquina por día

1. Editar `scripts/model.py` en `build_model()`:

```python
# Después de las restricciones R6...

# Nueva restricción: Máximo 3 cambios de setup por máquina por día
max_cambios = 3
for m, d in product(M, D):
    mdl.add_constraint(
        mdl.sum(w[(m,b1,b2,d,t)] for (mm,b1,b2,dd,t) in w_keys if (mm,dd) == (m,d))
        <= max_cambios,
        ctname=f"R_max_cambios[{m},{d}]"
    )
```

---

### Testing

**Tests unitarios** (crear carpeta `tests/`):

```python
# tests/test_validators.py
import pytest
from components.validators import DataValidator
import pandas as pd

def test_validate_turnos_valid():
    df = pd.DataFrame({
        'DIA': [1, 2, 3],
        'CANTIDAD DE TURNOS': [2, 2, 2]
    })
    is_valid, errors = DataValidator.validate_turnos(df)
    assert is_valid == True
    assert len(errors) == 0

def test_validate_turnos_invalid():
    df = pd.DataFrame({
        'DIA': [1, 2, -1],  # Día negativo (inválido)
        'CANTIDAD DE TURNOS': [2, 2, 2]
    })
    is_valid, errors = DataValidator.validate_turnos(df)
    assert is_valid == False
    assert len(errors) > 0
```

**Ejecutar tests:**
```bash
pip install pytest
pytest tests/
```

---

### Deploy en Producción

#### Opción 1: Streamlit Cloud

1. Subir código a GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. Conectar repositorio
4. Deploy automático

#### Opción 2: Azure Web App

```bash
# Crear requirements con versiones exactas
pip freeze > requirements.txt

# Crear archivo de configuración para Azure
# runtime.txt
python-3.13

# Procfile (para Gunicorn)
web: sh setup.sh && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

#### Opción 3: Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build y run
docker build -t modelo-cajas .
docker run -p 8501:8501 modelo-cajas
```

---

## 📊 Ejemplo de Flujo Completo

### Escenario: Planificar 5 días de producción

**Datos:**
- 6 máquinas (M1-M6)
- 3 tipos de caja (CAJA_A, CAJA_B, CAJA_C)
- 5 días
- 2 turnos/día (8h cada uno)
- Demanda: 500 cajas/día de cada tipo

**Paso 1: Preparar Datos**
1. Descargar templates
2. Editar en Excel:
   - `Turnos.csv`: 5 días, 2 turnos cada uno
   - `Disponibilidad_Maquinas.csv`: M1-M6 disponibles todos los días
   - `Productividad_Maquina_Caja.csv`:
     - M1-M3: 100 cajas/h para CAJA_A, 80 para CAJA_B, 90 para CAJA_C
     - M4-M6: 95, 85, 95
   - `Tiempo_de_Setup_por_maquina.csv`: 0.5h entre cambios
   - `Duracion_Turno.csv`: 8h todos los turnos

**Paso 2: Cargar y Validar**
1. Upload archivos en Configuración
2. Validación automática
3. Guardar datos

**Paso 3: Configurar Demanda**
1. En Optimización, editar demanda:
   - CAJA_A, Día 1-5: 500
   - CAJA_B, Día 1-5: 500
   - CAJA_C, Día 1-5: 500

**Paso 4: Optimizar**
1. Time limit: 120s
2. MIP gap: 1%
3. Ejecutar

**Resultado esperado:**
- Objetivo: ~15-20h de setup total
- Eficiencia: ~85-90%
- Cumplimiento: 100%
- Tiempo de ejecución: 30-60s

**Paso 5: Analizar**
1. Ver Gantt: distribución de asignaciones
2. Heatmap: utilización de máquinas
3. Tablas: filtrar por CAJA_A y ver qué máquinas la producen

**Paso 6: Exportar**
1. Excel completo para compartir con gerencia
2. CSV para análisis en Python/R
3. JSON para integrar con ERP

---

## 📞 Soporte y Contacto

**Problemas técnicos:**
- Crear issue en GitHub (si aplica)
- Email: [Tu email de contacto]

**Mejoras y sugerencias:**
- Contribuciones bienvenidas
- Fork del repositorio
- Pull requests

---

## 📜 Licencia

**Uso interno.** Todos los derechos reservados.

---

## 🙏 Agradecimientos

**Tecnologías utilizadas:**
- [Streamlit](https://streamlit.io/) - Framework web interactivo
- [IBM CPLEX Docplex](https://www.ibm.com/products/ilog-cplex-optimization-studio) - Optimización matemática
- [Plotly](https://plotly.com/) - Visualizaciones interactivas
- [Pandas](https://pandas.pydata.org/) - Manipulación de datos
- [NumPy](https://numpy.org/) - Computación numérica

---

## 📝 Changelog

### v1.0.0 (2025-10-07)
- ✨ Versión inicial
- ✅ Interfaz multipágina completa
- ✅ Validación automática de formato
- ✅ Templates descargables
- ✅ Visualizaciones interactivas
- ✅ Exportación múltiples formatos
- ✅ Historial de ejecuciones
- ✅ Documentación completa

---

**¿Listo para optimizar tu producción? 🚀**

```bash
streamlit run app.py
```

**http://localhost:8501**
