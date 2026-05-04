"""
data_processing.py
==================

Procesa el dataset crudo de Lentiamo (gafas graduadas) y genera el dataset
listo para entrenamiento.

Replica la lógica del notebook `notebooks/02_LimpiezaEDA.ipynb`:
- Limpieza inicial (drop columnas inútiles, duplicados, NaN críticos).
- Imputación inteligente (mediana por marca para numéricas, moda para categóricas).
- Reducción de multicolinealidad (drop calibre_total).
- Enriquecimiento experto de marcas (merge con marcas_tier.csv).
- Normalización categórica (color, material).
- Enriquecimiento opcional de materiales (materiales_tier.csv).
- Feature engineering (8 features derivadas).
- Renombre de columnas a nombres definitivos (tier → gama_marca, segmento → segmento_comercial).

Uso:
    python src/data_processing.py

Inputs:
    data/raw/lentiamo_graduadas.csv      (obligatorio)
    data/raw/marcas_tier.csv             (obligatorio, separador ';')
    data/raw/materiales_tier.csv         (opcional, separador ';')

Output:
    data/processed/lentiamo_graduadas_clean.csv

Notas de diseño:
    - NO se winsoriza el target: los precios altos son productos premium reales,
      no outliers. Recortarlos haría que el modelo infraestimase el segmento
      de mayor margen para una óptica.
    - log_precio se crea como target alternativo (no destructivo) para modelos
      lineales que asumen distribución normal de errores.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'raw'
PROC = ROOT / 'data' / 'processed'

CSV_INPUT = RAW / 'lentiamo_graduadas.csv'
CSV_MARCAS = RAW / 'marcas_tier.csv'
CSV_MATERIALES = RAW / 'materiales_tier.csv'  # opcional
CSV_OUTPUT = PROC / 'lentiamo_graduadas_clean.csv'

NUM_COLS_BASE = ['ancho_lente', 'ancho_puente', 'largo_varilla', 'calibre_total', 'peso']
CAT_COLS_BASE = ['genero', 'material_montura', 'forma', 'tipo_montura', 'color', 'talla']

MAPEO_COLOR = {
    'negro':        ['negro', 'black'],
    'marron':       ['marrón', 'marron', 'havana', 'café', 'brown', 'caoba'],
    'gris':         ['gris', 'grafito', 'grey', 'antracita', 'plomo'],
    'transparente': ['transparente', 'cristal', 'crystal', 'translúcido', 'translucido'],
    'azul':         ['azul', 'navy', 'blue'],
    'dorado':       ['dorado', 'oro', 'gold'],
    'plateado':     ['plateado', 'plata', 'silver'],
    'rojo':         ['rojo', 'red', 'burdeos', 'borgoña'],
    'rosa':         ['rosa', 'rosado', 'pink'],
    'verde':        ['verde', 'green', 'oliva'],
    'morado':       ['morado', 'violeta', 'purple', 'lila'],
    'blanco':       ['blanco', 'white', 'beige', 'crema', 'marfil'],
    'tortoise':     ['tortoise'],
}

RENAME_FINAL = {
    'tier':     'gama_marca',
    'segmento': 'segmento_comercial',
}


# ---------------------------------------------------------------------------
# Pasos del pipeline
# ---------------------------------------------------------------------------
def cargar(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f'Cargado: {path.name} → {df.shape}')
    return df


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columnas inútiles, duplicados y NaN en críticos."""
    for col in ('url', 'tipo', 'polarizadas'):
        if col in df.columns:
            df = df.drop(columns=col)

    antes = len(df)
    df = df.drop_duplicates(subset=['modelo']).copy()
    df = df.dropna(subset=['precio', 'marca']).copy()
    print(f'Limpieza: {antes} → {len(df)} filas (drop dups + dropna críticos)')
    return df


def imputar(df: pd.DataFrame) -> pd.DataFrame:
    """Numéricas: mediana por marca, fallback global. Categóricas: moda."""
    for c in NUM_COLS_BASE:
        if c in df.columns:
            mediana_marca = df.groupby('marca')[c].transform('median')
            df[c] = df[c].fillna(mediana_marca).fillna(df[c].median())
    for c in CAT_COLS_BASE:
        if c in df.columns:
            moda = df[c].mode()
            df[c] = df[c].fillna(moda.iloc[0] if len(moda) > 0 else 'Desconocido')
    return df


def reducir_multicolinealidad(df: pd.DataFrame) -> pd.DataFrame:
    """calibre_total es ~ 2*ancho_lente + ancho_puente → redundante."""
    if 'calibre_total' in df.columns:
        df = df.drop(columns=['calibre_total'])
    return df


def enriquecer_marcas(df: pd.DataFrame) -> pd.DataFrame:
    """Merge con marcas_tier.csv para añadir tier, segmento, pais_origen, precio_min/max."""
    if not CSV_MARCAS.exists():
        raise FileNotFoundError(f'Falta {CSV_MARCAS}. Genera con flujo Perplexity + NotebookLM.')

    marcas_tier = pd.read_csv(CSV_MARCAS, sep=';')
    print(f'Enriquecimiento marcas: {len(marcas_tier)} marcas clasificadas')

    df = df.merge(marcas_tier, on='marca', how='left')
    df['tier']        = df['tier'].fillna('gama_media')
    df['segmento']    = df['segmento'].fillna('moda_casual')
    df['pais_origen'] = df['pais_origen'].fillna('Desconocido')
    df['precio_min']  = df['precio_min'].fillna(0).astype(float)
    df['precio_max']  = df['precio_max'].fillna(0).astype(float)
    if 'notas' in df.columns:
        df = df.drop(columns=['notas'])
    return df


def normalizar_color(df: pd.DataFrame) -> pd.DataFrame:
    def _map(s):
        if pd.isna(s):
            return 'otro'
        s_low = str(s).lower()
        for canon, sinonimos in MAPEO_COLOR.items():
            if any(syn in s_low for syn in sinonimos):
                return canon
        return 'otro'
    df['color'] = df['color'].apply(_map)
    return df


def normalizar_material(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa todas las variantes 'Eco-friendly - X' en una sola categoría."""
    df['material_montura'] = df['material_montura'].apply(
        lambda x: 'Eco-friendly' if isinstance(x, str) and x.startswith('Eco-friendly') else x
    )
    return df


def enriquecer_materiales(df: pd.DataFrame) -> pd.DataFrame:
    """Merge opcional con materiales_tier.csv para añadir categoría/gama/peso del material."""
    if not CSV_MATERIALES.exists():
        print(f'ℹ {CSV_MATERIALES.name} no encontrado, se omite enriquecimiento de materiales.')
        return df

    mat = pd.read_csv(CSV_MATERIALES, sep=';')
    mat = mat.rename(columns={
        'material':  'material_montura',
        'categoria': 'categoria_material',
        'gama':      'gama_material',
    })
    cols_merge = ['material_montura', 'categoria_material', 'gama_material', 'peso_relativo']
    df = df.merge(mat[cols_merge], on='material_montura', how='left')
    df['categoria_material'] = df['categoria_material'].fillna('otro')
    df['gama_material']      = df['gama_material'].fillna('gama_media')
    df['peso_relativo']      = df['peso_relativo'].fillna('medio')
    print(f'Enriquecimiento materiales: {len(mat)} materiales clasificados')
    return df


def crear_log_target(df: pd.DataFrame) -> pd.DataFrame:
    """Target alternativo. NO se winsoriza el precio (decisión justificada en notebook 02)."""
    df['log_precio'] = np.log1p(df['precio'])
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Features derivadas con sentido de negocio."""
    df['aspect_ratio']       = df['ancho_lente'] / df['largo_varilla']
    df['area_aprox']         = df['ancho_lente'] * df['ancho_puente']
    df['densidad']           = df['peso'] / df['area_aprox']
    df['ancho_total']        = 2 * df['ancho_lente'] + df['ancho_puente']
    df['montura_completa']   = (df['tipo_montura'].str.contains('completa', case=False, na=False)
                                .astype(int))
    df['es_unisex']          = df['genero'].str.lower().eq('unisex').astype(int)
    df['color_basico']       = df['color'].isin(['negro', 'marron']).astype(int)
    df['material_eco']       = (df['material_montura'] == 'Eco-friendly').astype(int)

    df['precio_medio_marca'] = (df['precio_min'] + df['precio_max']) / 2
    df['precio_medio_marca'] = (df['precio_medio_marca']
                                .replace(0, np.nan)
                                .fillna(df['precio'].median()))
    return df


def renombrar_final(df: pd.DataFrame) -> pd.DataFrame:
    """Renombre canónico para coherencia con el notebook 03 y el resto del pipeline."""
    df.rename(columns={k: v for k, v in RENAME_FINAL.items() if k in df.columns}, inplace=True)
    return df


def reordenar(df: pd.DataFrame) -> pd.DataFrame:
    """Identificadores → features → targets."""
    ids   = ['modelo'] if 'modelo' in df.columns else []
    tgts  = [c for c in ('precio', 'log_precio') if c in df.columns]
    feats = [c for c in df.columns if c not in ids + tgts]
    return df[ids + feats + tgts]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)

    df = cargar(CSV_INPUT)
    df = limpiar(df)
    df = imputar(df)
    df = reducir_multicolinealidad(df)
    df = enriquecer_marcas(df)
    df = normalizar_color(df)
    df = normalizar_material(df)
    df = enriquecer_materiales(df)
    df = crear_log_target(df)
    df = feature_engineering(df)
    df = renombrar_final(df)
    df = reordenar(df)

    df.to_csv(CSV_OUTPUT, index=False)
    print(f'\n✅ Dataset procesado: {CSV_OUTPUT}')
    print(f'   {df.shape[0]} filas, {df.shape[1]} columnas')


if __name__ == '__main__':
    main()
