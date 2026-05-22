"""
gh3_sr_runner.py
======================================================
eml-sr によるシンボリック回帰実行モジュール
- Searcher を使って find_candidates で Pareto Front を取得
- RMSE で最良候補を選択
- タイムアウトや例外に対してロバストに動作
======================================================
"""

import time
import numpy as np
import eml_sr
from typing import Dict, Any, List


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error"""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def run_sr_on_equation(
    eq_id: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    max_complexity: int = 6,
    beam_width: int = 300,
    rmse_threshold: float = 1e-4,
) -> Dict[str, Any]:
    """
    1つの方程式に対してeml-srのシンボリック回帰を実行する。

    Parameters
    ----------
    eq_id : str          - 方程式ID (ログ用)
    X_train : ndarray    - 入力 (n_samples, n_vars)
    y_train : ndarray    - 出力 (n_samples,)
    max_complexity : int - eml-sr の最大複雑度
    beam_width : int     - ビーム幅
    rmse_threshold : float - 成功とみなすRMSE閾値

    Returns
    -------
    dict with keys: eq_id, status, found_formula, found_python, rmse,
                    complexity, elapsed_s, candidates
    """
    result_base = {
        "eq_id": eq_id,
        "status": "failed",
        "found_formula": None,
        "found_python": None,
        "rmse": None,
        "complexity": None,
        "elapsed_s": 0.0,
        "candidates": [],
    }

    try:
        n_samples, n_vars = X_train.shape
        inputs_list = X_train.tolist()
        targets_list = y_train.tolist()

        searcher = eml_sr.Searcher(max_complexity=max_complexity, beam_width=beam_width)

        start_t = time.time()

        # Pareto frontの候補を全て取得 (複数候補を比較)
        candidates = searcher.find_candidates(inputs_list, targets_list)

        elapsed = time.time() - start_t

        if not candidates:
            result_base["elapsed_s"] = elapsed
            result_base["status"] = "no_candidates"
            return result_base

        # 各候補のRMSEを計算して最良を選択
        best_cand = None
        best_rmse = float("inf")
        cand_infos = []

        for cand in candidates:
            try:
                preds = cand.predict(inputs_list)
                preds_arr = np.array(preds, dtype=float)
                if not np.all(np.isfinite(preds_arr)):
                    cand_rmse = float("inf")
                else:
                    cand_rmse = _rmse(y_train, preds_arr)

                cand_infos.append({
                    "formula": cand.formula,
                    "python": cand.to_python(),
                    "complexity": cand.complexity,
                    "rmse": cand_rmse if np.isfinite(cand_rmse) else None,
                    "error": float(cand.error) if hasattr(cand, "error") else None,
                })

                if cand_rmse < best_rmse:
                    best_rmse = cand_rmse
                    best_cand = cand
            except Exception:
                continue

        result_base["elapsed_s"] = elapsed
        result_base["candidates"] = cand_infos

        if best_cand is None:
            result_base["status"] = "prediction_failed"
            return result_base

        result_base["found_formula"] = best_cand.formula
        result_base["found_python"] = best_cand.to_python()
        result_base["complexity"] = best_cand.complexity
        result_base["rmse"] = best_rmse if np.isfinite(best_rmse) else None

        if np.isfinite(best_rmse) and best_rmse < rmse_threshold:
            result_base["status"] = "ok"
        elif np.isfinite(best_rmse) and best_rmse < rmse_threshold * 100:
            result_base["status"] = "partial"
        else:
            result_base["status"] = "failed"

        return result_base

    except Exception as e:
        result_base["status"] = "error"
        result_base["error_msg"] = str(e)
        return result_base
