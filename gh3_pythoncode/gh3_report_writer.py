"""
gh3_report_writer.py
======================================================
分析結果のレポート生成モジュール
- JSON形式の結果サマリからMarkdownレポートを生成
======================================================
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


def _status_emoji(status: str) -> str:
    return {
        "ok": "✅",
        "partial": "🟡",
        "failed": "❌",
        "skipped": "⏭️",
        "no_candidates": "🔲",
        "prediction_failed": "⚠️",
        "error": "💥",
    }.get(status, "❓")


def _format_rmse(rmse) -> str:
    if rmse is None:
        return "N/A"
    try:
        return f"{float(rmse):.3e}"
    except Exception:
        return str(rmse)


def write_report(summary: Dict[str, Any], report_path: str) -> None:
    """
    分析サマリからMarkdownレポートを生成する。

    Parameters
    ----------
    summary : dict - main() で生成した結果サマリ
    report_path : str - 出力先レポートパス
    """
    results = summary.get("results", [])
    total = summary.get("total", 0)
    ok_count = summary.get("ok", 0)
    skipped = summary.get("skipped", 0)
    failed = summary.get("failed", 0)
    total_elapsed = summary.get("total_elapsed_s", 0.0)
    settings = summary.get("settings", {})

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ステータス別集計
    status_counts: Dict[str, int] = {}
    for r in results:
        s = r.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    partial_count = status_counts.get("partial", 0)
    ok_rate = ok_count / total * 100 if total > 0 else 0.0
    ok_partial_rate = (ok_count + partial_count) / total * 100 if total > 0 else 0.0

    lines = []
    lines.append("# EML-SR Feynman Equations 全式推定 レポート")
    lines.append("")
    lines.append(f"**生成日時:** {now_str}  ")
    lines.append(f"**ブランチ:** `20260521_claude_allfunc_estimate`  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. 実験概要")
    lines.append("")
    lines.append("### 目的")
    lines.append("")
    lines.append(
        "Feynman Equations データセット（100式）に対して、**データのみ**からeml-srシンボリック回帰で"
        "数式を自動発見できるかをテストする。"
        "分析時は数式（正解）を「未知」として扱い、変数範囲から生成したランダムサンプルのみを入力とした。"
    )
    lines.append("")
    lines.append("### 使用ライブラリ")
    lines.append("")
    lines.append("| ライブラリ | 役割 |")
    lines.append("|-----------|------|")
    lines.append("| `eml_sr` (Rust製 Python bindings) | シンボリック回帰エンジン (EML演算子) |")
    lines.append("| `numpy` | 数値計算・データ生成 |")
    lines.append("| `pandas` | CSV読み込み |")
    lines.append("")
    lines.append("### 実験設定")
    lines.append("")
    lines.append("| パラメータ | 値 |")
    lines.append("|-----------|-----|")
    lines.append(f"| 訓練サンプル数 (N_SAMPLES) | {settings.get('N_SAMPLES', 'N/A')} |")
    lines.append(f"| 最大複雑度 (MAX_COMPLEXITY) | {settings.get('MAX_COMPLEXITY', 'N/A')} |")
    lines.append(f"| ビーム幅 (BEAM_WIDTH) | {settings.get('BEAM_WIDTH', 'N/A')} |")
    lines.append(f"| 成功RMSE閾値 | {settings.get('RMSE_THRESHOLD', 'N/A')} |")
    lines.append(f"| 合計実行時間 | {total_elapsed:.1f}s ({total_elapsed/60:.1f}min) |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. 総合結果サマリ")
    lines.append("")
    lines.append("| 指標 | 値 |")
    lines.append("|-----|-----|")
    lines.append(f"| 対象方程式数 | {total} |")
    lines.append(f"| ✅ 回収成功 (RMSE < {settings.get('RMSE_THRESHOLD', 1e-4):.0e}) | {ok_count} ({ok_rate:.1f}%) |")
    lines.append(f"| 🟡 部分的回収 (RMSE < {settings.get('RMSE_THRESHOLD', 1e-4)*100:.0e}) | {partial_count} ({partial_count/total*100:.1f}% ) |")
    lines.append(f"| ❌ 失敗 | {status_counts.get('failed', 0)} |")
    lines.append(f"| ⏭️ スキップ | {skipped} |")
    lines.append(f"| その他エラー | {status_counts.get('error', 0) + status_counts.get('no_candidates', 0) + status_counts.get('prediction_failed', 0)} |")
    lines.append(f"| **成功+部分計** | **{ok_count + partial_count} ({ok_partial_rate:.1f}%)** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. 各方程式の詳細結果")
    lines.append("")
    lines.append(
        "| # | 方程式ID | 変数数 | ステータス | RMSE | 複雑度 | 発見した数式 | 時間(s) |"
    )
    lines.append("|---|---------|--------|------------|------|--------|-------------|---------|")

    for r in results:
        idx = r.get("index", "?")
        eq_id = r.get("eq_id", "?")
        n_vars = r.get("n_vars", "?")
        status = r.get("status", "unknown")
        emoji = _status_emoji(status)
        rmse_str = _format_rmse(r.get("rmse"))
        complexity = r.get("complexity", "N/A")
        formula = r.get("found_formula") or "N/A"
        # 長い数式は省略
        if len(str(formula)) > 50:
            formula = str(formula)[:47] + "..."
        elapsed = r.get("elapsed_s", 0.0)
        elapsed_str = f"{elapsed:.2f}" if elapsed is not None else "N/A"

        lines.append(
            f"| {idx} | `{eq_id}` | {n_vars} | {emoji} {status} | {rmse_str} | {complexity} | `{formula}` | {elapsed_str} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. 成功した方程式の詳細")
    lines.append("")

    ok_results = [r for r in results if r.get("status") == "ok"]
    if ok_results:
        for r in ok_results:
            lines.append(f"### `{r['eq_id']}`")
            lines.append("")
            lines.append(f"- **変数:** {', '.join(r.get('var_names', []))}")
            lines.append(f"- **発見した式 (eml-sr):** `{r.get('found_formula', 'N/A')}`")
            lines.append(f"- **Python表現:** `{r.get('found_python', 'N/A')}`")
            lines.append(f"- **RMSE:** {_format_rmse(r.get('rmse'))}")
            lines.append(f"- **複雑度:** {r.get('complexity', 'N/A')}")
            lines.append(f"- **実行時間:** {r.get('elapsed_s', 0):.2f}s")
            lines.append("")
    else:
        lines.append("成功した方程式はありませんでした。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 5. 部分的回収の方程式")
    lines.append("")

    partial_results = [r for r in results if r.get("status") == "partial"]
    if partial_results:
        for r in partial_results:
            lines.append(f"### `{r['eq_id']}`")
            lines.append("")
            lines.append(f"- **変数:** {', '.join(r.get('var_names', []))}")
            lines.append(f"- **発見した式 (eml-sr):** `{r.get('found_formula', 'N/A')}`")
            lines.append(f"- **RMSE:** {_format_rmse(r.get('rmse'))}")
            lines.append(f"- **複雑度:** {r.get('complexity', 'N/A')}")
            lines.append("")
    else:
        lines.append("部分的に回収された方程式はありませんでした。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 6. 考察")
    lines.append("")
    lines.append("### 6.1 EML演算子の特性")
    lines.append("")
    lines.append(
        "EML (Exponential-Modular-Logarithmic) 演算子は、指数関数・対数関数を含む複合関数を"
        "低複雑度で表現できる特徴を持つ。これにより、物理方程式に頻出する"
        "`exp`, `log`, `sqrt`, 積・商などのパターンを効率的に探索できる。"
    )
    lines.append("")
    lines.append("### 6.2 変数数と難易度")
    lines.append("")
    lines.append(
        "変数数が増えるほど探索空間が指数的に広がるため、多変数方程式での回収率が"
        "低下する傾向が予想される。"
        "今回の実験でも、変数数の多い方程式（5変数以上）での成功率が低い傾向が"
        "見られたかどうかを以下の表で確認できる。"
    )
    lines.append("")

    # 変数数別集計
    var_stats: Dict[int, Dict[str, int]] = {}
    for r in results:
        nv = r.get("n_vars", 0)
        st = r.get("status", "unknown")
        if nv not in var_stats:
            var_stats[nv] = {"ok": 0, "total": 0}
        var_stats[nv]["total"] += 1
        if st == "ok":
            var_stats[nv]["ok"] += 1

    lines.append("| 変数数 | 対象数 | 成功数 | 成功率 |")
    lines.append("|--------|--------|--------|--------|")
    for nv in sorted(var_stats.keys()):
        t = var_stats[nv]["total"]
        o = var_stats[nv]["ok"]
        rate = o / t * 100 if t > 0 else 0
        lines.append(f"| {nv} | {t} | {o} | {rate:.0f}% |")

    lines.append("")
    lines.append("### 6.3 設定の影響と改善可能性")
    lines.append("")
    lines.append(
        f"- **MAX_COMPLEXITY={settings.get('MAX_COMPLEXITY', 'N/A')}:** "
        "複雑度を上げることで発見できる式の範囲が広がるが、計算コストも増大する。"
    )
    lines.append(
        f"- **BEAM_WIDTH={settings.get('BEAM_WIDTH', 'N/A')}:** "
        "ビーム幅を広げると多様な候補を保持できるが、メモリ・時間コストが増加する。"
    )
    lines.append(
        f"- **N_SAMPLES={settings.get('N_SAMPLES', 'N/A')}:** "
        "サンプル数を増やすと数値的安定性が向上するが、探索時間も増加する。"
    )
    lines.append("")
    lines.append("### 6.4 まとめ")
    lines.append("")
    lines.append(
        f"今回の実験では、{total}個のFeynman方程式に対して"
        f"eml-srが **{ok_count}式({ok_rate:.1f}%)** を正確に回収した。"
        f"部分的な近似も含めると **{ok_count + partial_count}式({ok_partial_rate:.1f}%)** に達する。"
        f"EML演算子の特性により、単純な多項式や指数・対数を含む式では高い回収率が期待でき、"
        f"今後のパラメータ調整（複雑度・サンプル数の増加）によるさらなる向上も見込まれる。"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本レポートは `gh3_claude_allfunc_estimate_sr.py` により自動生成されました。*")
    lines.append("")

    report_text = "\n".join(lines)

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
