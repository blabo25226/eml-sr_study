"""
gh3_claude_allfunc_estimate_sr.py
======================================================
Feynman 方程式のシンボリック回帰 (eml-sr) による全式推定
- データは FeynmanEquations.csv の変数範囲から生成
- 推定時はフォーミュラを「未知」として扱う
- 結果は gh3_sr_results.json に保存し、レポート生成に利用する
======================================================
"""

import sys
import os

# このファイルのディレクトリ（gh3_pythoncode）を基準にする
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, SCRIPT_DIR)

from gh3_data_generator import load_equations, generate_dataset
from gh3_sr_runner import run_sr_on_equation
from gh3_report_writer import write_report

import json
import time

# ===== 設定 =====
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "FeynmanEquations.csv")
RESULTS_PATH = os.path.join(SCRIPT_DIR, "gh3_sr_results.json")
REPORT_PATH = os.path.join(PROJECT_ROOT, "texts", "claude_allfunc_estimate_sr_report.md")

N_SAMPLES = 200          # 訓練サンプル数
MAX_COMPLEXITY = 6       # eml-sr の最大複雑度（Level6≈10s/式）
BEAM_WIDTH = 300         # ビーム幅
RMSE_THRESHOLD = 1e-4    # "回収成功" とみなすRMSE閾値


def main():
    print("=" * 60)
    print("  EML-SR: Feynman Equations – All Function Estimation")
    print("=" * 60)

    # --- 1. 方程式リストの読み込み ---
    equations = load_equations(CSV_PATH)
    print(f"[INFO] Loaded {len(equations)} equations from CSV")

    results = []
    ok_count = 0
    total_start = time.time()

    # --- 2. 各方程式に対してSRを実行 ---
    for idx, eq in enumerate(equations):
        eq_id = eq["filename"]
        n_vars = eq["n_vars"]
        var_names = eq["var_names"]
        var_ranges = eq["var_ranges"]

        print(f"\n[{idx+1:03d}/{len(equations)}] {eq_id}  (vars={n_vars})")

        # データ生成（数式は使わず範囲のみ使用；yはCSVの数式で計算するが解析時は「未知」）
        X_train, y_train = generate_dataset(eq, N_SAMPLES, seed=42 + idx)

        # NaN / Inf チェック
        import numpy as np
        if np.any(~np.isfinite(y_train)):
            bad_count = np.sum(~np.isfinite(y_train))
            print(f"  [WARN] {bad_count}/{N_SAMPLES} non-finite y values – filtering")
            mask = np.isfinite(y_train)
            X_train = X_train[mask]
            y_train = y_train[mask]

        if len(y_train) < 10:
            print(f"  [SKIP] too few valid samples ({len(y_train)})")
            results.append({
                "index": idx + 1,
                "eq_id": eq_id,
                "n_vars": n_vars,
                "var_names": var_names,
                "status": "skipped",
                "reason": "too_few_valid_samples",
                "found_formula": None,
                "found_python": None,
                "rmse": None,
                "complexity": None,
                "elapsed_s": 0.0,
                "candidates": []
            })
            continue

        # SR実行
        result = run_sr_on_equation(
            eq_id=eq_id,
            X_train=X_train,
            y_train=y_train,
            max_complexity=MAX_COMPLEXITY,
            beam_width=BEAM_WIDTH,
            rmse_threshold=RMSE_THRESHOLD,
        )
        result["index"] = idx + 1
        result["n_vars"] = n_vars
        result["var_names"] = var_names
        results.append(result)

        status_str = result.get("status", "unknown")
        rmse_val = result.get("rmse", float("nan"))
        found = result.get("found_formula", "N/A")
        elapsed = result.get("elapsed_s", 0.0)

        print(f"  Found:   {found}")
        print(f"  RMSE:    {rmse_val:.3e}  Status: {status_str}  Time: {elapsed:.2f}s")

        if status_str == "ok":
            ok_count += 1

    total_elapsed = time.time() - total_start

    # --- 3. 結果をJSONに保存 ---
    summary = {
        "total": len(equations),
        "ok": ok_count,
        "skipped": sum(1 for r in results if r.get("status") == "skipped"),
        "failed": sum(1 for r in results if r.get("status") not in ("ok", "skipped")),
        "total_elapsed_s": total_elapsed,
        "settings": {
            "N_SAMPLES": N_SAMPLES,
            "MAX_COMPLEXITY": MAX_COMPLEXITY,
            "BEAM_WIDTH": BEAM_WIDTH,
            "RMSE_THRESHOLD": RMSE_THRESHOLD,
        },
        "results": results,
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] Results saved to {RESULTS_PATH}")

    # --- 4. レポート生成 ---
    write_report(summary, REPORT_PATH)
    print(f"[INFO] Report written to {REPORT_PATH}")

    print("\n" + "=" * 60)
    print(f"  SUMMARY: {ok_count} / {len(equations)} equations recovered")
    print(f"  Total time: {total_elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
