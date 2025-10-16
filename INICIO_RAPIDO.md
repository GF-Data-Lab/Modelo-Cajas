# 🚀 Inicio Rápido - Sistema de Optimización de Cajas

## ✅ Requisitos Completados

- ✅ Python 3.11.4 instalado
- ✅ Entorno virtual `venv311` creado
- ✅ Dependencias instalándose...

## 📝 Cómo Iniciar la Aplicación

### Opción 1: Usando el Script (Recomendado)

Simplemente haz doble clic en:
```
start_app.bat
```

### Opción 2: Manualmente

```bash
# 1. Activar entorno virtual
venv311\Scripts\activate

# 2. Iniciar aplicación
streamlit run app.py
```

## 🌐 Acceder a la Aplicación

Después de ejecutar, la aplicación estará disponible en:
- http://localhost:8501

## 📋 Flujo de Uso

### 1️⃣ Cargar Archivos
- Ve a la página "📤 Cargar Archivos"
- Sube `Parametros.xlsx`
- Sube `Libro7.xlsx` (demanda)
- Verifica que ambos se validen correctamente ✅

### 2️⃣ Ejecutar Modelo
- Ve a la página "🚀 Ejecutar Modelo"
- Selecciona una planta:
  - MOSTAZAL
  - MALLOA
  - MOLINA
- Haz clic en "▶️ Ejecutar Modelo de Optimización"
- Espera 2-5 minutos

### 3️⃣ Ver Resultados
- Ve a la página "📊 Resultados"
- Explora:
  - Métricas clave (KPIs)
  - Gráficos interactivos
  - Análisis de variables
  - Estadísticas

## 🔧 Comandos Útiles

### Instalar IBM Watson ML (si falta)
```bash
venv311\Scripts\activate
pip install ibm-watson-machine-learning
```

### Actualizar dependencias
```bash
venv311\Scripts\activate
pip install -r requirements.txt --upgrade
```

### Verificar versión de Python
```bash
venv311\Scripts\python --version
# Debe mostrar: Python 3.11.4
```

## ❓ Solución de Problemas

### La aplicación no inicia
```bash
# Verificar que el entorno esté activado
venv311\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de módulo no encontrado
```bash
# Activar entorno
venv311\Scripts\activate

# Instalar el módulo faltante
pip install <nombre-modulo>
```

### Error de IBM Watson ML
- Verifica que estés usando Python 3.11 (NO 3.13)
- Verifica credenciales en `run_model.py`
- Verifica conexión a internet

## 📦 Archivos Importantes

- `start_app.bat` - Script para iniciar la aplicación
- `venv311/` - Entorno virtual Python 3.11
- `requirements.txt` - Lista de dependencias
- `app.py` - Aplicación principal
- `run_model.py` - Script de ejecución del modelo

## 🎯 Características del Sistema

✅ Interfaz web interactiva con Streamlit
✅ Validación automática de archivos Excel
✅ Filtrado por planta
✅ Ejecución en IBM Watson ML
✅ Visualizaciones con Plotly
✅ Análisis estadístico (EDA)
✅ Exportación de resultados
✅ Logo y estilos corporativos

## 📞 Ayuda

Si tienes problemas:
1. Verifica que estés usando el entorno venv311
2. Lee los mensajes de error en la consola
3. Revisa `README_FLUJO_ACTUALIZADO.md`
4. Contacta al equipo de desarrollo

---

**Última actualización:** Octubre 2025
**Python:** 3.11.4
**Sistema:** Garces Data Analytics
