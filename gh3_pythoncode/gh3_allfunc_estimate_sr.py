import pandas as pd
import numpy as np
import time
import eml_sr
import traceback

def rmse(actual, predicted):
    """RMSE（二乗平均平方根誤差）を計算"""
    return np.sqrt(np.mean((np.array(actual) - np.array(predicted)) ** 2))

def evaluate_formula(formula_str, env):
    # Some formulas in the dataset might have symbols like x**2 instead of x^2 (Python uses **)
    # Replace math operators if necessary, but looks like they are Python-compatible in the dataset.
    try:
        return eval(formula_str, {"__builtins__": None}, env)
    except Exception as e:
        # print(f"Error evaluating formula '{formula_str}': {e}")
        return None

def main():
    print("===========================================================")
    print("  Feynman SR Complete Test (eml-sr Python API)")
    print("===========================================================\n")

    try:
        df = pd.read_csv('data/FeynmanEquations.csv')
    except FileNotFoundError:
        print("Error: 'FeynmanEquations.csv' が見つかりません。")
        return

    # Filter out empty rows
    df = df.dropna(subset=['Filename', 'Formula'])
    
    n_samples = 64
    beam_width = 100
    max_complexity = 6
    
    results = []
    
    # 組み込みの数学関数
    base_env = {
        "exp": np.exp,
        "sqrt": np.sqrt,
        "sin": np.sin,
        "cos": np.cos,
        "arcsin": np.arcsin,
        "arccos": np.arccos,
        "tan": np.tan,
        "tanh": np.tanh,
        "ln": np.log,  # natural log
        "log": np.log,
        "pi": np.pi
    }

    start_total = time.time()
    
    for index, row in df.iterrows():
        eq_id = row['Filename']
        formula = row['Formula']
        output_var = row['Output']
        n_vars = int(row['# variables'])

        # 変数情報の抽出
        vars_info = []
        for i in range(1, n_vars + 1):
            name = row.get(f'v{i}_name')
            if pd.isna(name) or str(name).strip() == '':
                continue
            low = float(row.get(f'v{i}_low', 1.0))
            high = float(row.get(f'v{i}_high', 5.0))
            vars_info.append({'name': str(name).strip(), 'low': low, 'high': high})
            
        print(f"\n--- [{index+1}/{len(df)}] {eq_id} ---")
        print(f"Expected: {output_var} = {formula}")

        np.random.seed(42 + index)
        inputs = []
        targets = []
        
        valid_points = 0
        attempts = 0
        while valid_points < n_samples and attempts < n_samples * 10:
            attempts += 1
            point = []
            local_env = base_env.copy()
            for v in vars_info:
                val = np.random.uniform(v['low'], v['high'])
                point.append(val)
                local_env[v['name']] = val
            
            y = evaluate_formula(formula, local_env)
            if y is not None and not np.isnan(y) and not np.isinf(y):
                # We need complex support for some operations, but EML-SR uses real numbers. Let's just use real results.
                if isinstance(y, complex):
                    if np.isclose(y.imag, 0):
                        y = y.real
                    else:
                        continue
                inputs.append(point)
                targets.append(float(y))
                valid_points += 1
                
        if len(inputs) < n_samples:
            print(f"Skipped {eq_id}: Could not generate {n_samples} valid data points (generated {len(inputs)}).")
            results.append({
                "id": eq_id,
                "expected": formula,
                "found": "FAILED (Data generation)",
                "rmse": None,
                "time": 0.0,
                "status": "FAIL_DATA"
            })
            continue
            
        # Run search
        searcher = eml_sr.Searcher(max_complexity=max_complexity, beam_width=beam_width)
        
        t0 = time.time()
        try:
            res = searcher.fit(inputs, targets)
            preds = res.predict(inputs)
            current_rmse = rmse(targets, preds)
            formula_found = res.formula
        except Exception as e:
            print(f"Error during search: {e}")
            current_rmse = float('inf')
            formula_found = f"ERROR: {e}"
            
        t1 = time.time()
        
        elapsed = t1 - t0
        status = "OK" if current_rmse < 1e-5 else "FAIL"
        
        print(f"Found: {formula_found}")
        print(f"RMSE:  {current_rmse:.6e}")
        print(f"Time:  {elapsed:.4f}s")
        print(f"Status: {status}")
        
        results.append({
            "id": eq_id,
            "expected": formula,
            "found": formula_found,
            "rmse": current_rmse,
            "time": elapsed,
            "status": status
        })
        
    end_total = time.time()
    print(f"\n===========================================================")
    print(f"Finished evaluating {len(df)} equations in {end_total - start_total:.2f}s")
    
    # Generate Report
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    
    report = [
        "# eml-sr All Function Estimation Report\n",
        f"**Total Equations Evaluated:** {len(results)}",
        f"**Successfully Recovered (RMSE < 1e-5):** {ok_count}",
        f"**Failed:** {len(results) - ok_count}",
        f"**Total Time:** {end_total - start_total:.2f}s\n",
        "## Successes\n",
        "| ID | Expected Formula | Found Formula | RMSE | Time (s) |",
        "|---|---|---|---|---|"
    ]
    
    for r in results:
        if r['status'] == 'OK':
            report.append(f"| {r['id']} | `{r['expected']}` | `{r['found']}` | {r['rmse']:.2e} | {r['time']:.2f} |")
            
    report.append("\n## Failures & Errors\n")
    report.append("| ID | Expected Formula | Found Formula | RMSE | Status | Time (s) |")
    report.append("|---|---|---|---|---|---|")
    
    for r in results:
        if r['status'] != 'OK':
            rmse_str = f"{r['rmse']:.2e}" if r['rmse'] is not None else "N/A"
            report.append(f"| {r['id']} | `{r['expected']}` | `{r['found']}` | {rmse_str} | {r['status']} | {r['time']:.2f} |")
            
    with open("texts/allfunc_estimate_sr_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Report generated at texts/allfunc_estimate_sr_report.md")

if __name__ == "__main__":
    main()
