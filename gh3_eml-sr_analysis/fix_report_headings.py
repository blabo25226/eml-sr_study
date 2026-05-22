"""
fix_report_headings.py
セクション7の各見出し ### `EQ_ID` （変数: ...）に正しい数式を追記する
"""
import re

# ---- CSVから正しい数式マップを構築 ----
import pandas as pd
df = pd.read_csv("data/FeynmanEquations.csv").dropna(subset=["Filename","Formula"])
df = df[df["Filename"].str.strip() != ""]
formula_map = {str(row["Filename"]).strip(): str(row["Formula"]).strip()
               for _, row in df.iterrows()}

# ---- レポートを読む ----
with open("texts/allfunc_moreestimate_sr_report.md", encoding="utf-8") as f:
    lines = f.readlines()

# ---- セクション7の範囲を特定 ----
# 見出しパターン: ### `EQ_ID` （変数: ...）
heading_pattern = re.compile(r'^(### `([^`]+)`)( .+)?$')

new_lines = []
in_sec7 = False
changed = 0

for i, line in enumerate(lines):
    stripped = line.rstrip('\r\n')

    # セクション7開始検出
    if stripped.startswith("## 7."):
        in_sec7 = True
    elif stripped.startswith("## 8."):
        in_sec7 = False

    if in_sec7:
        m = heading_pattern.match(stripped)
        if m:
            eq_id = m.group(2)          # e.g. "III.15.14"
            rest  = m.group(3) or ""    # e.g. " （変数: h, E_n, d）"

            if eq_id in formula_map:
                correct = formula_map[eq_id]
                # 正しい数式をバッククォートで付加
                new_heading = f"{m.group(1)}  — 正しい数式: `{correct}`{rest}"
                eol = '\r\n' if '\r\n' in line else '\n'
                new_lines.append(new_heading + eol)
                changed += 1
                continue

    new_lines.append(line)

# ---- 書き戻す ----
with open("texts/allfunc_moreestimate_sr_report.md", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Done. {changed} headings updated.")
