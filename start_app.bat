@echo off
echo ============================================
echo   Sistema de Optimizacion de Cajas
echo   Python 3.11 + IBM Watson ML
echo ============================================
echo.

REM Activar entorno virtual Python 3.11
call venv311\Scripts\activate.bat

echo [OK] Entorno Python 3.11 activado
echo.

REM Iniciar Streamlit
echo Iniciando Streamlit...
streamlit run app.py

pause
