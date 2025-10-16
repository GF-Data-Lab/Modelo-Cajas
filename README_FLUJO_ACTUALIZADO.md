# 📦 Sistema de Optimización de Cajas - Flujo Actualizado

## 🎯 Descripción General

Sistema completo para optimizar la asignación de producción de cajas en plantas industriales, con interfaz web interactiva y análisis detallado de resultados.

## 🚀 Flujo de Trabajo

```
┌─────────────────────────────────────────┐
│  1️⃣  CARGAR ARCHIVOS                    │
│  📤 Subir y validar datos               │
│                                          │
│  • Parametros.xlsx (configuración)      │
│  • Libro7.xlsx (demanda)                │
│  • Validación automática                │
│  • Resumen de plantas y datos           │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│  2️⃣  EJECUTAR MODELO                    │
│  🚀 Seleccionar planta y optimizar      │
│                                          │
│  • Seleccionar planta (dropdown)        │
│  • Ver información de la planta         │
│  • Ejecutar optimización                │
│  • Monitoreo de progreso                │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│  3️⃣  VER RESULTADOS                     │
│  📊 Análisis y visualización            │
│                                          │
│  • Métricas clave (KPIs)                │
│  • Gráficos interactivos                │
│  • Análisis estadístico                 │
│  • Exportar resultados                  │
└─────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
Modelo-Cajas/
├── app.py                              # Aplicación principal
├── run_model.py                        # Script de ejecución del modelo
├── utils.py                            # Utilidades (logo, etc.)
├── requirements.txt                    # Dependencias
│
├── pages/                              # Páginas de la aplicación
│   ├── 01_📤_Cargar_Archivos.py       # Carga y validación
│   ├── 02_🚀_Ejecutar_Modelo.py       # Selección y ejecución
│   ├── 03_📊_Resultados.py            # Visualización y análisis
│   └── _old/                           # Páginas antiguas (archivadas)
│
├── styles/                             # Estilos y recursos
│   ├── common_styles.py                # Estilos compartidos
│   ├── COLOR_REFERENCE.md              # Guía de colores
│   └── garces_data_analytics.png       # Logo
│
├── inputs/                             # Datos de entrada
│   ├── Parametros.xlsx                 # Configuración de plantas
│   ├── Libro7.xlsx                     # Datos de demanda
│   └── csv/                            # CSVs generados (temporal)
│
├── scripts/
│   └── model.py                        # Modelo de optimización CPLEX
│
├── outputs/                            # Resultados
│   ├── solution.json                   # Solución del modelo
│   └── log.txt                         # Log de ejecución
│
└── README_FLUJO_ACTUALIZADO.md         # Este archivo
```

## 📋 Páginas de la Aplicación

### 1️⃣ Cargar Archivos (`01_📤_Cargar_Archivos.py`)

**Función:** Subir y validar archivos de entrada

**Características:**
- ✅ Upload de archivos Excel
- ✅ Validación automática de estructura
- ✅ Detección de errores y advertencias
- ✅ Vista previa de datos
- ✅ Resumen de plantas disponibles
- ✅ Métricas de demanda

**Validaciones:**

**Parametros.xlsx:**
- Hojas requeridas: Planta, Turnos, Disponibilidad Maquinas, Productividad Máquina_Caja, Tiempo de Setup, Duracion Turno
- Columnas específicas por hoja
- Datos no vacíos

**Libro7.xlsx:**
- Columnas requeridas: DES_PLANTA, DESC_ESPECIE, DESC_VARIEDAD, DESC_ENVASE, cajas_asignadas, fecha_planificación
- Validación de tipos de datos
- Datos no vacíos

### 2️⃣ Ejecutar Modelo (`02_🚀_Ejecutar_Modelo.py`)

**Función:** Seleccionar planta y ejecutar optimización

**Características:**
- ✅ Verifica que los archivos estén cargados
- ✅ Selector de planta (MOSTAZAL, MALLOA, MOLINA)
- ✅ Información detallada de la planta:
  - Número de máquinas
  - Días de planificación
  - Tipos de caja
  - Registros de demanda
- ✅ Botón de ejecución con monitoreo
- ✅ Visualización de logs en tiempo real
- ✅ Historial de ejecuciones

**Proceso de Ejecución:**
1. Filtrado de datos por planta
2. Generación de CSVs
3. Empaquetado (tar.gz)
4. Upload a IBM Watson ML
5. Ejecución del solver CPLEX
6. Descarga de resultados

### 3️⃣ Resultados (`03_📊_Resultados.py`)

**Función:** Visualización y análisis de resultados

**Características:**

**📈 Métricas Clave:**
- Valor de función objetivo
- Tiempo de solución
- Variables activas
- Estado de la solución

**📊 Visualizaciones:**
- Gráfico de barras (Top 20 variables)
- Distribución de valores (histograma)
- Análisis por tipo de variable (pastel)
- Tablas interactivas

**🔍 Análisis:**
- Búsqueda y filtrado de variables
- Estadísticas descriptivas
- Clasificación por tipo
- Exportación a CSV

**📝 Información Adicional:**
- Log completo del solver
- Resumen ejecutivo
- Datos crudos (JSON)

## 🛠️ Instalación y Uso

### 1. Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd Modelo-Cajas

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecución

```bash
# Iniciar aplicación web
streamlit run app.py
```

La aplicación se abrirá en: http://localhost:8501

### 3. Uso del Sistema

**Paso 1: Cargar Archivos**
1. Ve a la página "📤 Cargar Archivos"
2. Sube `Parametros.xlsx`
3. Sube `Libro7.xlsx`
4. Verifica que ambos archivos sean validados ✅

**Paso 2: Ejecutar Modelo**
1. Ve a la página "🚀 Ejecutar Modelo"
2. Selecciona una planta del dropdown
3. Revisa la información de la planta
4. Haz clic en "▶️ Ejecutar Modelo de Optimización"
5. Espera 2-5 minutos

**Paso 3: Ver Resultados**
1. Ve a la página "📊 Resultados"
2. Explora las métricas y gráficos
3. Filtra y analiza variables
4. Descarga resultados si necesitas

## 📊 Datos de Entrada

### Parametros.xlsx

Archivo con 6 hojas:

1. **Planta**: Lista de plantas (MOSTAZAL, MALLOA, MOLINA)
2. **Turnos**: Cantidad de turnos por día y planta
3. **Disponibilidad Maquinas**: Disponibilidad por día, planta y máquina
4. **Productividad Máquina_Caja**: Productividad (cajas/hora) por máquina y tipo
5. **Tiempo de Setup por máquina**: Tiempo de cambio entre tipos de caja
6. **Duracion Turno**: Horas por turno

### Libro7.xlsx

Archivo con demanda de cajas:

- **DES_PLANTA**: Nombre de la planta
- **DESC_ESPECIE**: Especie del producto
- **DESC_VARIEDAD**: Variedad del producto
- **DESC_ENVASE**: Tipo de envase/caja
- **cajas_asignadas**: Cantidad de cajas a producir
- **fecha_planificación**: Fecha de planificación
- Y otras columnas auxiliares...

## 📈 Resultados

### solution.json

Archivo JSON con la solución óptima:
- Variables de decisión
- Valores de las variables
- Estado de la solución
- Valor objetivo
- Tiempo de ejecución

### log.txt

Log detallado de la ejecución del solver CPLEX:
- Progreso de la optimización
- Iteraciones
- Bounds (superior/inferior)
- Gap de optimalidad
- Mensajes del solver

## 🎨 Características de la Interfaz

### ✨ Estilos Unificados
- Logo de Garces Data Analytics
- Colores corporativos consistentes
- Diseño profesional y limpio

### 📱 Responsive
- Funciona en diferentes tamaños de pantalla
- Layout adaptable

### 🔄 Interactivo
- Gráficos interactivos con Plotly
- Filtros dinámicos
- Tabs y expanders
- Búsqueda en tiempo real

### 💾 Session State
- Datos persistentes durante la sesión
- No se pierden al cambiar de página
- Flujo de trabajo continuo

## ⚠️ Notas Importantes

### Python Version
- **Recomendado**: Python 3.11 o 3.12
- **No compatible**: Python 3.13 (problema con ibm-watson-machine-learning)

### IBM Watson ML
- Requiere conexión a internet
- Credenciales configuradas en `run_model.py`
- API Key y Space ID válidos

### Archivos Temporales
- CSVs generados en `inputs/csv/`
- `modelo.tar.gz` se recrea en cada ejecución
- `solution.json` y `log.txt` se sobrescriben

## 🐛 Solución de Problemas

### Error: "Module not found: ibm_watson_machine_learning"
```bash
pip install ibm-watson-machine-learning
```
**Nota:** Si usas Python 3.13, considera cambiar a Python 3.11 o 3.12

### Error: "No se encontraron plantas"
- Verifica que `Parametros.xlsx` tenga la hoja "Planta"
- Verifica que la columna se llame "PLANTA"

### Error: "Archivos NO cargados"
- Ve primero a la página "Cargar Archivos"
- Sube ambos archivos Excel
- Verifica que la validación sea exitosa ✅

### El modelo tarda mucho
- Tiempo estimado: 2-5 minutos
- Depende del tamaño de los datos
- Depende de la complejidad del problema
- Timeout configurado: 10 minutos

## 📞 Soporte

Para problemas o consultas:
- Revisa este README
- Revisa `README_SISTEMA_PLANTAS.md`
- Contacta al equipo de desarrollo

---

**Desarrollado por**: Equipo Garces Data Analytics
**Versión**: 2.0 - Flujo Actualizado
**Fecha**: Octubre 2025
**Tecnologías**: Streamlit, Plotly, CPLEX, IBM Watson ML
