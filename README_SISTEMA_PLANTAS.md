# Sistema de Optimización de Cajas por Planta

## Descripción General

Este sistema permite seleccionar una planta específica (MOSTAZAL, MALLOA, o MOLINA) y ejecutar el modelo de optimización de cajas filtrando automáticamente todos los parámetros y demanda por la planta seleccionada.

## Archivos de Entrada

### 1. `inputs/Libro7.xlsx`
- Contiene la **demanda** de cajas
- Columnas importantes:
  - `DES_PLANTA`: Nombre de la planta
  - `cajas_asignadas`: Cantidad de cajas asignadas
  - `fecha_planificación`: Fecha de planificación
- Actualmente tiene datos para la planta MOLINA

### 2. `inputs/Parametros.xlsx`
- Contiene los **parámetros** del modelo
- Hojas:
  - **Planta**: Lista de plantas disponibles (MOSTAZAL, MALLOA, MOLINA)
  - **Turnos**: Cantidad de turnos por día y planta
  - **Disponibilidad Maquinas**: Disponibilidad de máquinas por día, planta y máquina
  - **Productividad Máquina_Caja**: Productividad de cada máquina por tipo de caja y planta
  - **Tiempo de Setup por máquina**: Tiempos de cambio entre tipos de caja por planta
  - **Duracion Turno**: Duración de cada turno por día y planta

## Componentes del Sistema

### 1. Interfaz Web (Streamlit)

#### Página Principal: `app.py`
- Dashboard principal con métricas generales
- Incluye logo de Garces Data Analytics
- Estilos unificados

#### Página de Selección: `pages/00_🏭_Seleccionar_Planta.py`
- Permite seleccionar una planta del listado disponible
- Muestra información de la planta seleccionada
- Botón para ejecutar el modelo
- Monitorea el progreso de la ejecución

### 2. Motor de Optimización: `run_model.py`

Este script realiza todo el proceso de optimización:

1. **Carga de Datos**: Lee archivos Excel de parámetros y demanda
2. **Filtrado por Planta**: Filtra todos los datos por la planta seleccionada
3. **Generación de CSVs**: Convierte las hojas Excel a archivos CSV
4. **Empaquetado**: Crea un archivo `modelo.tar.gz` con todos los datos
5. **Ejecución en IBM Watson ML**:
   - Sube el modelo a IBM Watson Machine Learning
   - Ejecuta la optimización
   - Descarga los resultados (`solution.json` y `log.txt`)

## Uso

### Opción 1: Interfaz Web (Recomendado)

```bash
streamlit run app.py
```

1. En el navegador, ve a la página "🏭 Seleccionar Planta"
2. Selecciona una planta del dropdown
3. Haz clic en "▶️ Ejecutar Optimización"
4. Espera a que el proceso termine (2-5 minutos)
5. Revisa los resultados en `solution.json` y `log.txt`

### Opción 2: Línea de Comandos

```bash
python run_model.py <PLANTA>
```

Ejemplos:
```bash
python run_model.py MOLINA
python run_model.py MOSTAZAL
python run_model.py MALLOA
```

Si no especificas la planta, el script mostrará las plantas disponibles:
```bash
python run_model.py
```

## Estructura de Directorios

```
Modelo-Cajas/
├── app.py                           # Aplicación principal Streamlit
├── run_model.py                     # Script de ejecución del modelo
├── utils.py                         # Utilidades (show_logo)
├── requirements.txt                 # Dependencias Python
├── inputs/
│   ├── Libro7.xlsx                  # Archivo de demanda
│   ├── Parametros.xlsx              # Archivo de parámetros
│   └── csv/                         # CSVs generados (automático)
├── pages/
│   ├── 00_🏭_Seleccionar_Planta.py # Página de selección de planta
│   ├── 01_📊_Configuración.py      # Página de configuración
│   ├── 02_🔧_Optimización.py       # Página de optimización
│   ├── 03_📈_Resultados.py         # Página de resultados
│   └── 04_📥_Exportar.py           # Página de exportación
├── styles/
│   ├── common_styles.py             # Estilos compartidos
│   ├── COLOR_REFERENCE.md           # Referencia de colores
│   └── garces_data_analytics.png    # Logo
├── scripts/
│   └── model.py                     # Modelo de optimización CPLEX
├── outputs/                         # Resultados (automático)
├── solution.json                    # Solución del modelo (generado)
└── log.txt                          # Log de ejecución (generado)
```

## Flujo de Procesamiento

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SELECCIÓN DE PLANTA                                      │
│    - Usuario selecciona planta en interfaz Streamlit        │
│    - Plantas disponibles: MOSTAZAL, MALLOA, MOLINA          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PROCESAMIENTO DE DATOS                                   │
│    - Leer Libro7.xlsx (demanda)                            │
│    - Leer Parametros.xlsx (parámetros)                     │
│    - Filtrar todos los datos por planta seleccionada       │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. GENERACIÓN DE CSVs                                       │
│    - demanda.csv                                            │
│    - Turnos.csv                                             │
│    - Disponibilidad_Maquinas.csv                            │
│    - Productividad_Maquina_Caja.csv                         │
│    - Tiempo_de_Setup_por_maquina.csv                        │
│    - Duracion_Turno.csv                                     │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. EMPAQUETADO                                              │
│    - Crear modelo.tar.gz con:                               │
│      * model.py (modelo CPLEX)                              │
│      * Todos los CSVs generados                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. EJECUCIÓN EN IBM WATSON ML                               │
│    - Subir modelo.tar.gz a Watson ML                        │
│    - Crear deployment                                       │
│    - Ejecutar optimización (CPLEX)                          │
│    - Monitorear progreso                                    │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. DESCARGA DE RESULTADOS                                   │
│    - solution.json (solución óptima)                        │
│    - log.txt (registro de ejecución)                        │
└─────────────────────────────────────────────────────────────┘
```

## Resultados

### `solution.json`
Contiene la solución óptima del modelo con:
- Asignaciones de máquinas por día, turno y tipo de caja
- Tiempos de setup calculados
- Métricas de optimización

### `log.txt`
Contiene el registro de ejecución del solver CPLEX con:
- Estado del modelo
- Progreso de la optimización
- Estadísticas finales
- Posibles warnings o errores

## Requisitos

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0
docplex>=2.25.0
numpy>=1.24.0
python-dateutil>=2.8.0
ibm-watson-machine-learning>=1.0.0
```

Instalar con:
```bash
pip install -r requirements.txt
```

## Credenciales IBM Watson ML

Las credenciales están configuradas en `run_model.py`:
- **API Key**: Configurada en `WML_API_KEY`
- **Space ID**: Configurado en `SPACE_ID`
- **URL**: Configurada en `WML_URL`

⚠️ **Importante**: Estas credenciales son sensibles. No las compartas públicamente.

## Características Principales

✅ **Selección de Planta**: Interfaz intuitiva para seleccionar la planta
✅ **Filtrado Automático**: Todos los datos se filtran por planta automáticamente
✅ **Validación de Datos**: Verificación de archivos y columnas antes de ejecutar
✅ **Monitoreo en Tiempo Real**: Seguimiento del progreso de ejecución
✅ **Estilos Unificados**: Interfaz consistente con logo y colores corporativos
✅ **Manejo de Errores**: Mensajes claros de error y warnings
✅ **Logs Detallados**: Registro completo del proceso de ejecución

## Resolución de Problemas

### Error: "No module named 'ibm_watson_machine_learning'"
```bash
pip install ibm-watson-machine-learning
```

### Error: "No se encontró inputs/Parametros.xlsx"
Verifica que el archivo existe en la carpeta `inputs/`

### Error: "No hay datos de demanda para PLANTA_X"
Verifica que Libro7.xlsx tiene datos para esa planta en la columna `DES_PLANTA`

### La optimización tarda mucho
El tiempo de ejecución depende de:
- Tamaño de los datos
- Complejidad del modelo
- Recursos de IBM Watson ML

Tiempo estimado: 2-5 minutos

## Soporte

Para problemas o mejoras, contacta al equipo de desarrollo.

---

**Desarrollado por**: Equipo Garces Data Analytics
**Versión**: 1.0
**Fecha**: Octubre 2025
