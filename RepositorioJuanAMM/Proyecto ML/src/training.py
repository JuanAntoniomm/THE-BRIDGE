"""
training.py
===========

Entrena el modelo final (RandomForest) sobre el dataset procesado y lo guarda
en `models/final_model.pkl`. También genera los splits train/test que usa
`evaluation.py`.

Replica la lógica de `notebooks/03_Modelado.ipynb` con las decisiones tomadas
tras el análisis de ablaciones y VIF:

- Familia ganadora: árboles (RandomForestRegressor).
- Target: precio en € (los árboles no necesitan log).
- Features finales (5 numéricas + 10-13 categóricas según disponibilidad):
    Numéricas: ancho_lente, ancho_puente, largo_varilla, peso, precio_medio_marca.
    Categóricas: marca, genero, material_montura, forma, tipo_montura, color, talla,
                 gama_marca, segmento_comercial, pais_origen,
                 (+ categoria_material, gama_material, peso_relativo si existen).
- Hiperparámetros optimizados con GridSearchCV (5-fold).
- Métrica de selección: MAE (interpretable en € para negocio).

Uso:
    python src/training.py

Inputs:
    data/processed/lentiamo_graduadas_clean.csv

Outputs:
    data/train/train.csv
    data/test/test.csv
    models/final_model.pkl
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / 'data' / 'processed'
TRAIN = ROOT / 'data' / 'train'
TEST = ROOT / 'data' / 'test'
MODELS_DIR = ROOT / 'models'

CSV_INPUT = PROC / 'lentiamo_graduadas_clean.csv'
MODEL_OUTPUT = MODELS_DIR / 'final_model.pkl'

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_SPLITS = 5

# Features finales (justificación en notebook 03 sec. 7-9)
NUM_FINAL = [
    'ancho_lente',
    'ancho_puente',
    'largo_varilla',
    'peso',
    'precio_medio_marca',
]
CAT_FINAL = [
    'marca', 'genero', 'material_montura', 'forma', 'tipo_montura',
    'color', 'talla',
    'gama_marca', 'segmento_comercial', 'pais_origen',
    'categoria_material', 'gama_material', 'peso_relativo',  # opcionales
]

PARAM_GRID = {
    'm__n_estimators':     [200, 400],
    'm__max_depth':        [None, 15, 25],
    'm__min_samples_leaf': [1, 3],
    'm__max_features':     ['sqrt', 0.5],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def existing(cols, df):
    """Devuelve solo las columnas que existen realmente en df."""
    return [c for c in cols if c in df.columns]


def build_preprocessor(num_cols, cat_cols):
    """ColumnTransformer para árboles: imputación + OneHot (sin escalar numéricas)."""
    num_pipe = Pipeline([('imputer', SimpleImputer(strategy='median'))])
    cat_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot',  OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])
    return ColumnTransformer(
        [('num', num_pipe, num_cols), ('cat', cat_pipe, cat_cols)],
        remainder='drop',
        verbose_feature_names_out=False,
    )


# ---------------------------------------------------------------------------
# Pasos
# ---------------------------------------------------------------------------
def cargar_y_renombrar(path: Path) -> pd.DataFrame:
    """Carga el dataset procesado y aplica renombre defensivo (por compatibilidad)."""
    df = pd.read_csv(path)
    rename_map = {'tier': 'gama_marca', 'segmento': 'segmento_comercial'}
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    print(f'Cargado: {path.name} → {df.shape}')
    return df


def split_y_guardar(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    TRAIN.mkdir(parents=True, exist_ok=True)
    TEST.mkdir(parents=True, exist_ok=True)
    train_df, test_df = train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    train_df.to_csv(TRAIN / 'train.csv', index=False)
    test_df.to_csv(TEST / 'test.csv', index=False)
    print(f'Split: train={len(train_df)} | test={len(test_df)}')
    return train_df, test_df


def entrenar_con_gridsearch(X_train: pd.DataFrame, y_train: pd.Series,
                             num_cols: list, cat_cols: list) -> GridSearchCV:
    pipe = Pipeline([
        ('prep', build_preprocessor(num_cols, cat_cols)),
        ('m',    RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1)),
    ])
    cv = KFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    gs = GridSearchCV(
        pipe,
        param_grid=PARAM_GRID,
        cv=cv,
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        verbose=1,
    )
    print('\nLanzando GridSearchCV (RandomForest)...')
    gs.fit(X_train, y_train)
    print(f'\nMejores hiperparámetros:')
    for k, v in gs.best_params_.items():
        print(f'  · {k}: {v}')
    print(f'MAE en CV (mejor): {-gs.best_score_:.2f} €')
    return gs


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = cargar_y_renombrar(CSV_INPUT)
    train_df, _ = split_y_guardar(df)

    num_cols = existing(NUM_FINAL, train_df)
    cat_cols = existing(CAT_FINAL, train_df)
    print(f'\nFeatures usadas:')
    print(f'  num ({len(num_cols)}): {num_cols}')
    print(f'  cat ({len(cat_cols)}): {cat_cols}')

    X_train = train_df[num_cols + cat_cols]
    y_train = train_df['precio']

    gs = entrenar_con_gridsearch(X_train, y_train, num_cols, cat_cols)

    joblib.dump(gs.best_estimator_, MODEL_OUTPUT)
    print(f'\n✅ Modelo guardado: {MODEL_OUTPUT}')


if __name__ == '__main__':
    main()
