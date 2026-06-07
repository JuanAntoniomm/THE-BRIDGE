@echo off
REM ============================================================
REM  Script para crear un entorno virtual con Python 3.11
REM  e instalar todo lo necesario para los ejercicios de DL.
REM ============================================================

echo.
echo === [1/4] Comprobando que Python 3.11 esta disponible ===
py -3.11 --version
if errorlevel 1 (
    echo.
    echo ERROR: No se encuentra Python 3.11.
    echo Instalalo desde https://www.python.org/downloads/release/python-3119/
    echo y marca la casilla "Add Python to PATH".
    pause
    exit /b 1
)

echo.
echo === [2/4] Creando entorno virtual en .venv ===
if exist .venv (
    echo El entorno .venv ya existe, lo reutilizo.
) else (
    py -3.11 -m venv .venv
    if errorlevel 1 (
        echo ERROR creando el entorno virtual.
        pause
        exit /b 1
    )
)

echo.
echo === [3/4] Actualizando pip e instalando dependencias ===
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR instalando dependencias.
    pause
    exit /b 1
)

echo.
echo === [4/4] Registrando el kernel en Jupyter ===
python -m ipykernel install --user --name dl-intro --display-name "Python 3.11 (DL Intro)"

echo.
echo ============================================================
echo  LISTO. Para usarlo:
echo  1. Abre el notebook Deep_Learning_regression.ipynb
echo  2. En la esquina superior derecha (o menu Kernel),
echo     selecciona el kernel: "Python 3.11 (DL Intro)"
echo  3. Ejecuta las celdas.
echo ============================================================
echo.
pause
