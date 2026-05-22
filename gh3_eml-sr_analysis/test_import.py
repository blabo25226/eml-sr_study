import sys, os
sys.path.insert(0, 'gh3_eml-sr_analysis')

# Import the module to test it
import importlib.util
spec = importlib.util.spec_from_file_location("m", "gh3_eml-sr_analysis/gh3_allfunc_moreestimate_sr.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

eqs = m.load_equations('data/FeynmanEquations.csv')
print(f'Loaded {len(eqs)} equations')
X, y = m.generate_dataset(eqs[7], 20, 42)
print(f'I.12.1 X={X.shape} y[:3]={y[:3]}')
