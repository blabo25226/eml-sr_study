"""Quick test: run SR on first 3 equations"""
import sys
sys.path.insert(0, 'gh3_pythoncode')
from gh3_data_generator import load_equations, generate_dataset
from gh3_sr_runner import run_sr_on_equation
import os
import numpy as np

csv_path = os.path.join('data', 'FeynmanEquations.csv')
eqs = load_equations(csv_path)

# Test on first 3 simple equations
for eq in eqs[:3]:
    fn = eq["filename"]
    print(f"\n=== {fn} ({eq['n_vars']} vars) ===")
    X, y = generate_dataset(eq, 100, seed=42)
    result = run_sr_on_equation(fn, X, y, max_complexity=6, beam_width=300)
    print(f"  Status:  {result['status']}")
    print(f"  Formula: {result['found_formula']}")
    print(f"  RMSE:    {result['rmse']}")
    print(f"  Time:    {result['elapsed_s']:.2f}s")
    print(f"  Num candidates: {len(result['candidates'])}")
