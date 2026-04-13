from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr, shapiro, spearmanr

NO_EMANCIPADOS = (
    "Hijos/Hijas no del padre o madre solos",
    "Hijos/Hijas del padre o madre solos",
)

MAPA_SEXO = {
    "Hombres": "Hombre",
    "Mujeres": "Mujer",
}

ALIASES_COLUMNAS = {
    "Comunidades y Ciudades Autónomas": (
        "Comunidades y Ciudades Autónomas",
        "Comunidades y Ciudades AutÃ³nomas",
    ),
    "Situación en el hogar": (
        "Situación en el hogar",
        "SituaciÃ³n en el hogar",
    ),
    "Total Nacional": ("Total Nacional",),
    "Grupo de edad": ("Grupo de edad",),
    "Edad del trabajador": ("Edad del trabajador",),
    "Sexo": ("Sexo",),
    "Total": ("Total",),
    "periodo": ("periodo", "Periodo"),
    "Periodo": ("Periodo", "periodo"),
}


def _ensure_list(values: str | Sequence[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    return list(values)


def _resolve_column_name(columns: Iterable[str], column: str) -> str:
    available = list(columns)
    aliases = ALIASES_COLUMNAS.get(column, (column,))
    for candidate in aliases:
        if candidate in available:
            return candidate
    if column in available:
        return column
    raise KeyError(f"No se encontro la columna '{column}'. Columnas disponibles: {available}")


def _resolve_if_present(columns: Iterable[str], column: str) -> str | None:
    try:
        return _resolve_column_name(columns, column)
    except KeyError:
        return None


def eliminar_columnas(
    df: pd.DataFrame,
    columnas: Sequence[str],
    *,
    inplace: bool = False,
) -> pd.DataFrame:
    result = df if inplace else df.copy()
    columns_to_drop: list[str] = []
    for column in columnas:
        resolved = _resolve_if_present(result.columns, column)
        if resolved is not None and resolved not in columns_to_drop:
            columns_to_drop.append(resolved)
    if columns_to_drop:
        result.drop(columns=columns_to_drop, inplace=True)
    return result


def convertir_columna_numerica(
    serie: pd.Series,
    *,
    miles: bool = False,
    abs_values: bool = False,
    remove_thousands_sep: bool = False,
    integer: bool = False,
) -> pd.Series:
    cleaned = serie.astype(str).str.strip()
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    if remove_thousands_sep:
        cleaned = cleaned.str.replace(".", "", regex=False)
    cleaned = cleaned.str.replace(",", ".", regex=False)

    numeric = pd.to_numeric(cleaned, errors="coerce")

    if miles:
        numeric = numeric * 1000
    if abs_values:
        numeric = numeric.abs()
    if integer:
        return numeric.round().astype("Int64")
    return numeric


def normalizar_sexo(
    df: pd.DataFrame,
    columna: str = "Sexo",
    *,
    mapping: dict[str, str] | None = None,
    inplace: bool = False,
) -> pd.DataFrame:
    result = df if inplace else df.copy()
    column_name = _resolve_column_name(result.columns, columna)
    result[column_name] = result[column_name].replace(mapping or MAPA_SEXO)
    return result


def clasificar_emancipacion(
    df: pd.DataFrame,
    columna_hogar: str = "Situación en el hogar",
    *,
    columna_salida: str = "Emancipado",
    categorias_no: Sequence[str] = NO_EMANCIPADOS,
    inplace: bool = False,
) -> pd.DataFrame:
    result = df if inplace else df.copy()
    hogar_col = _resolve_column_name(result.columns, columna_hogar)
    result[columna_salida] = np.where(
        result[hogar_col].isin(categorias_no),
        "No emancipado",
        "Si emancipado",
    )
    return result


def generar_tabla_emancipacion(
    df: pd.DataFrame,
    keys: Sequence[str],
    *,
    value_col: str = "Total",
    category_col: str = "Emancipado",
) -> pd.DataFrame:
    group_keys = [_resolve_column_name(df.columns, key) for key in keys]
    value_key = _resolve_column_name(df.columns, value_col)
    category_key = _resolve_column_name(df.columns, category_col)

    grouped = (
        df.groupby(group_keys + [category_key], as_index=False)[value_key]
        .sum()
    )

    result = (
        grouped.pivot_table(
            index=group_keys,
            columns=category_key,
            values=value_key,
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    result.columns.name = None
    return result


def calcular_porcentajes_emancipacion(
    df: pd.DataFrame,
    *,
    col_si: str = "Si emancipado",
    col_no: str = "No emancipado",
    decimals: int = 3,
    inplace: bool = False,
) -> pd.DataFrame:
    result = df if inplace else df.copy()

    for column in (col_si, col_no):
        if column not in result.columns:
            result[column] = 0

    total = result[col_si].fillna(0) + result[col_no].fillna(0)
    denominator = total.replace(0, np.nan)

    result[f"{col_si}%"] = (result[col_si] / denominator * 100).round(decimals)
    result[f"{col_no}%"] = (result[col_no] / denominator * 100).round(decimals)
    return result


def limpiar_emancipacion(
    df: pd.DataFrame,
    *,
    con_genero: bool = True,
    categorias_no: Sequence[str] = NO_EMANCIPADOS,
) -> pd.DataFrame:
    result = eliminar_columnas(df, ["Grupo de edad", "Total Nacional"])
    if not con_genero:
        result = eliminar_columnas(result, ["Sexo"])

    total_col = _resolve_column_name(result.columns, "Total")
    result[total_col] = convertir_columna_numerica(
        result[total_col],
        miles=True,
        integer=True,
    )

    result = clasificar_emancipacion(result, categorias_no=categorias_no)

    keys = ["Comunidades y Ciudades Autónomas", "periodo"]
    if con_genero and _resolve_if_present(result.columns, "Sexo") is not None:
        keys.insert(1, "Sexo")

    result = generar_tabla_emancipacion(result, keys=keys, value_col=total_col)
    return calcular_porcentajes_emancipacion(result)


def limpiar_salario(
    df: pd.DataFrame,
    *,
    con_genero: bool = True,
) -> pd.DataFrame:
    result = eliminar_columnas(df, ["Edad del trabajador"])
    if not con_genero:
        result = eliminar_columnas(result, ["Sexo"])

    total_col = _resolve_column_name(result.columns, "Total")
    result[total_col] = convertir_columna_numerica(
        result[total_col],
        remove_thousands_sep=True,
        abs_values=True,
    )

    if con_genero and _resolve_if_present(result.columns, "Sexo") is not None:
        result = normalizar_sexo(result)

    return result


def merge_emancipacion_salario(
    df_emanc: pd.DataFrame,
    df_sal: pd.DataFrame,
    *,
    con_genero: bool = False,
    emancipation_col: str = "No emancipado%",
    salary_label: str | None = None,
    how: str = "inner",
) -> pd.DataFrame:
    comunidad_emanc = _resolve_column_name(df_emanc.columns, "Comunidades y Ciudades Autónomas")
    comunidad_sal = _resolve_column_name(df_sal.columns, "Comunidades y Ciudades Autónomas")
    periodo_emanc = _resolve_column_name(df_emanc.columns, "periodo")
    periodo_sal = _resolve_column_name(df_sal.columns, "Periodo")

    left_on = [comunidad_emanc, periodo_emanc]
    right_on = [comunidad_sal, periodo_sal]
    selected = [comunidad_emanc, periodo_emanc]

    if con_genero:
        sexo_emanc = _resolve_column_name(df_emanc.columns, "Sexo")
        sexo_sal = _resolve_column_name(df_sal.columns, "Sexo")
        left_on.insert(1, sexo_emanc)
        right_on.insert(1, sexo_sal)
        selected.insert(1, sexo_emanc)

    merged = df_emanc.merge(
        df_sal,
        left_on=left_on,
        right_on=right_on,
        how=how,
    )

    emancipation_key = _resolve_column_name(merged.columns, emancipation_col)
    salary_key = _resolve_column_name(merged.columns, "Total")

    result = merged[selected + [emancipation_key, salary_key]].copy()
    result = result.rename(
        columns={
            salary_key: salary_label or ("Sueldo medio anual" if con_genero else "Salario medio anual")
        }
    )

    sort_cols = [periodo_emanc, comunidad_emanc]
    if con_genero:
        sort_cols.append(_resolve_column_name(result.columns, "Sexo"))

    return result.sort_values(sort_cols).reset_index(drop=True)


def _result_to_frame(result: Any, group_values: dict[str, Any]) -> pd.DataFrame:
    if isinstance(result, pd.DataFrame):
        frame = result.copy()
    elif isinstance(result, pd.Series):
        frame = result.to_frame().T
    elif isinstance(result, dict):
        frame = pd.DataFrame([result])
    else:
        frame = pd.DataFrame([{"resultado": result}])

    insert_at = 0
    for column, value in group_values.items():
        if column in frame.columns:
            frame[column] = value
        else:
            frame.insert(insert_at, column, value)
            insert_at += 1

    return frame.reset_index(drop=True)


def aplicar_por_grupos(
    df: pd.DataFrame,
    group_cols: str | Sequence[str] | None,
    funcion: Callable[..., Any],
    *,
    dropna: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    groups = [_resolve_column_name(df.columns, column) for column in _ensure_list(group_cols)]

    if not groups:
        return _result_to_frame(funcion(df.copy(), **kwargs), {})

    frames: list[pd.DataFrame] = []
    for group_keys, data in df.groupby(groups, dropna=dropna, sort=True):
        if not isinstance(group_keys, tuple):
            group_keys = (group_keys,)
        group_values = dict(zip(groups, group_keys))
        frames.append(_result_to_frame(funcion(data.copy(), **kwargs), group_values))

    if not frames:
        return pd.DataFrame(columns=groups)

    return pd.concat(frames, ignore_index=True)


def test_normalidad(
    df: pd.DataFrame,
    columnas: Sequence[str],
    *,
    group_cols: str | Sequence[str] | None = None,
) -> pd.DataFrame:
    resolved_columns = [_resolve_column_name(df.columns, column) for column in columnas]

    def _test(data: pd.DataFrame) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for column in resolved_columns:
            values = pd.to_numeric(data[column], errors="coerce").dropna()
            if len(values) >= 3:
                stat, pvalue = shapiro(values)
            else:
                stat, pvalue = np.nan, np.nan
            result[f"{column}_stat"] = stat
            result[f"{column}_pvalue"] = pvalue
            result[f"{column}_n"] = len(values)
        return result

    return aplicar_por_grupos(df, group_cols, _test)


def calcular_correlacion(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    metodo: str = "pearson",
    group_cols: str | Sequence[str] | None = None,
) -> pd.DataFrame:
    x_col = _resolve_column_name(df.columns, x)
    y_col = _resolve_column_name(df.columns, y)

    corr_functions = {
        "pearson": pearsonr,
        "spearman": spearmanr,
    }
    if metodo not in corr_functions:
        raise ValueError(f"Metodo no soportado: {metodo}")

    def _correlate(data: pd.DataFrame) -> dict[str, Any]:
        values = data[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(values) >= 2:
            corr, pvalue = corr_functions[metodo](values[x_col], values[y_col])
        else:
            corr, pvalue = np.nan, np.nan
        return {
            "metodo": metodo,
            "r": corr,
            "pvalue": pvalue,
            "n": len(values),
        }

    return aplicar_por_grupos(df, group_cols, _correlate)


def calcular_correlaciones(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    group_cols: str | Sequence[str] | None = None,
    metodos: Sequence[str] = ("pearson", "spearman"),
) -> pd.DataFrame:
    frames = [
        calcular_correlacion(df, x, y, metodo=metodo, group_cols=group_cols)
        for metodo in metodos
    ]
    return pd.concat(frames, ignore_index=True)


def ajustar_regresion_lineal(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    group_cols: str | Sequence[str] | None = None,
    add_constant: bool = True,
) -> pd.DataFrame:
    x_col = _resolve_column_name(df.columns, x)
    y_col = _resolve_column_name(df.columns, y)

    def _fit(data: pd.DataFrame) -> dict[str, Any]:
        values = data[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(values) < 2:
            return {
                "modelo": None,
                "n": len(values),
                "r2": np.nan,
                "coef_intercepto": np.nan,
                f"coef_{x_col}": np.nan,
                f"pvalue_{x_col}": np.nan,
            }

        x_data = values[[x_col]]
        if add_constant:
            x_data = sm.add_constant(x_data, has_constant="add")

        model = sm.OLS(values[y_col], x_data).fit()
        return {
            "modelo": model,
            "n": len(values),
            "r2": model.rsquared,
            "coef_intercepto": model.params.get("const", np.nan),
            f"coef_{x_col}": model.params.get(x_col, np.nan),
            f"pvalue_{x_col}": model.pvalues.get(x_col, np.nan),
        }

    return aplicar_por_grupos(df, group_cols, _fit)


__all__ = [
    "NO_EMANCIPADOS",
    "MAPA_SEXO",
    "ajustar_regresion_lineal",
    "aplicar_por_grupos",
    "calcular_correlacion",
    "calcular_correlaciones",
    "calcular_porcentajes_emancipacion",
    "clasificar_emancipacion",
    "convertir_columna_numerica",
    "eliminar_columnas",
    "generar_tabla_emancipacion",
    "limpiar_emancipacion",
    "limpiar_salario",
    "merge_emancipacion_salario",
    "normalizar_sexo",
    "test_normalidad",
]
