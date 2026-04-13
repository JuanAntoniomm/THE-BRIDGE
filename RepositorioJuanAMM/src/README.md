# Relación entre salario y emancipación juvenil en España (2018–2020)

Este proyecto analiza la relación entre el salario medio anual y la proporción de jóvenes no emancipados en España, utilizando datos por comunidad autónoma entre 2018 y 2020.

El objetivo es identificar si existe una relación estadísticamente significativa entre ambas variables y explorar diferencias por género.

## 📁 Datos
Fuentes de datos:
- Encuesta de estructura salarial (INE)
- Encuesta continua de hogares (INE)

Se utilizan dos variables principales:

- Emancipación juvenil
- Salario medio anual

Versiones utilizadas:

- Con desagregación por sexo
- Sin desagregación por sexo

Los datos han sido preprocesados para:

- Convertir formatos numéricos
- Agrupar categorías de emancipación
- Calcular proporciones relativas (%)

## ⚙️ Metodología

El análisis se divide en tres fases:

### 1. Limpieza y transformación

- Conversión de variables numéricas
- Agrupación en "Emancipado / No emancipado"
- Cálculo de porcentajes

### 2. Análisis exploratorio (EDA)

- Evolución temporal por CCAA
- Comparación por género
- Rankings territoriales

### 3. Análisis estadístico

- Test de normalidad (Shapiro-Wilk)
- Correlación de Pearson y Spearman
- Modelos de regresión lineal (OLS)

## 📊 Resultados

### 📉 Relación entre salario y no emancipación

Se observa una relación negativa entre el salario medio anual y la proporción de población no emancipada.

Las comunidades con mayor salario presentan menores niveles de no emancipación.

### 📊 Correlación

Los coeficientes de correlación de Pearson muestran:

- 2018: r = -0.64
- 2019: r = -0.71
- 2020: r = -0.61

Todos los resultados son estadísticamente significativos (p < 0.05).

### 📈 Modelo de regresión

El modelo de regresión lineal indica:

- Relación negativa consistente entre salario y no emancipación
- Un aumento de 1000€ en salario se asocia con ≈ 1–1.5% menos de no emancipados
- R² entre 0.37 y 0.50 (capacidad explicativa moderada)


### 👩‍🦰👨 Diferencias por género

El efecto del salario es más fuerte en mujeres:

- Mayor correlación negativa
- Mayor R² en los modelos

## 🧠 Conclusiones

- Existe una relación inversa significativa entre salario y emancipación
- El salario es un factor relevante pero no suficiente
- Otros factores como vivienda, cultura familiar o mercado laboral influyen
- El efecto es más fuerte en mujeres que en hombres

## 🗂️ Estructura

- `data/` → datasets
- `Memoria.ipynb` → notebook principal del análisis
- `Notebook/` → pruebas y análisis auxiliares
- `utils/` → funciones auxiliares (limpieza, estadística, gráficos)

## 🛠️ Tecnologías

- Python
- Pandas
- Seaborn / Matplotlib
- SciPy
- Statsmodels

## ▶️ Ejecución

1. Clonar el repositorio
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar el notebook principal (`Memoria.ipynb`)
