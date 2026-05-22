"""Test script for data generator"""
import sys
sys.path.insert(0, 'gh3_pythoncode')
from gh3_data_generator import load_equations, generate_dataset
import os

csv_path = os.path.join('data', 'FeynmanEquations.csv')
eqs = load_equations(csv_path)
print(f'Loaded {len(eqs)} equations')
print('First 3:')
for eq in eqs[:3]:
    fn = eq["filename"]
    nv = eq["n_vars"]
    vn = eq["var_names"]
    print(f'  {fn} | vars={nv} | {vn}')
    X, y = generate_dataset(eq, 10, seed=42)
    print(f'  X shape={X.shape}, y sample={y[:3]}')
