"""
gh3_data_generator.py
======================================================
Feynman 方程式のデータ生成モジュール
- CSV から方程式メタ情報を読み込む
- 変数範囲からランダムサンプルを生成する
- 数式の評価（正解ラベル生成）を行う
======================================================
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple


def load_equations(csv_path: str) -> List[Dict[str, Any]]:
    """
    FeynmanEquations.csv を読み込み、有効な方程式のリストを返す。
    """
    df = pd.read_csv(csv_path)
    # 空行除去
    df = df.dropna(subset=["Filename", "Formula"])
    df = df[df["Filename"].str.strip() != ""]

    equations = []
    for _, row in df.iterrows():
        filename = str(row["Filename"]).strip()
        formula = str(row["Formula"]).strip()
        output_var = str(row["Output"]).strip()
        n_vars = int(row["# variables"])

        var_names = []
        var_ranges = []
        for i in range(1, n_vars + 1):
            name_col = f"v{i}_name"
            low_col = f"v{i}_low"
            high_col = f"v{i}_high"
            if name_col in row and pd.notna(row[name_col]):
                var_names.append(str(row[name_col]).strip())
                var_ranges.append((float(row[low_col]), float(row[high_col])))

        if len(var_names) != n_vars:
            continue  # 不整合な行はスキップ

        equations.append({
            "filename": filename,
            "formula": formula,
            "output_var": output_var,
            "n_vars": n_vars,
            "var_names": var_names,
            "var_ranges": var_ranges,
        })

    return equations


def _build_eval_env() -> Dict[str, Any]:
    """数式evalのための安全な環境を構築する"""
    return {
        "exp": np.exp,
        "sqrt": np.sqrt,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "arcsin": np.arcsin,
        "arccos": np.arccos,
        "arctan": np.arctan,
        "arctan2": np.arctan2,
        "log": np.log,
        "ln": np.log,
        "abs": np.abs,
        "tanh": np.tanh,
        "sinh": np.sinh,
        "cosh": np.cosh,
        "pi": np.pi,
        "e": np.e,
        "__builtins__": None,
    }


def generate_dataset(
    eq: Dict[str, Any],
    n_samples: int,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    方程式情報とサンプル数から訓練データを生成する。

    Parameters
    ----------
    eq : dict  - load_equations() の要素
    n_samples : int - 生成するサンプル数
    seed : int - 乱数シード

    Returns
    -------
    X : (n_valid, n_vars) ndarray
    y : (n_valid,) ndarray
    """
    rng = np.random.default_rng(seed)
    formula = eq["formula"]
    var_names = eq["var_names"]
    var_ranges = eq["var_ranges"]
    n_vars = eq["n_vars"]

    base_env = _build_eval_env()

    X_list = []
    y_list = []

    # 最大 n_samples * 3 回試行してフィルタリング
    max_attempts = n_samples * 5
    attempt = 0

    while len(y_list) < n_samples and attempt < max_attempts:
        attempt += 1
        point = []
        local_env = base_env.copy()

        for i, (name, (low, high)) in enumerate(zip(var_names, var_ranges)):
            val = rng.uniform(low, high)
            point.append(val)
            local_env[name] = val

        try:
            y = float(eval(formula, {"__builtins__": None}, local_env))
            if np.isfinite(y):
                X_list.append(point)
                y_list.append(y)
        except Exception:
            continue

    X = np.array(X_list, dtype=float)
    y = np.array(y_list, dtype=float)
    return X, y
