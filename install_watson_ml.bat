@echo off
echo ============================================
echo   Instalando IBM Watson Machine Learning
echo   Python 3.11
echo ============================================
echo.

REM Activar entorno virtual Python 3.11
call venv311\Scripts\activate.bat

echo [OK] Entorno Python 3.11 activado
echo.

REM Instalar ibm-watson-machine-learning
echo Instalando ibm-watson-machine-learning...
pip install ibm-watson-machine-learning

echo.
echo ============================================
echo   Instalacion completada
echo ============================================
echo.

pause
