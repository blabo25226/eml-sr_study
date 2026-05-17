import numpy as np
from pyeml import discover

# Feed it data — it discovers the exact formula
x = np.linspace(0.1, 2.0, 200)
y = np.exp(x)

result = discover(x, y, max_depth=3)
print(result.expression)      # "exp(x)"
print(result.eml_expression)  # "eml(x, 1)"
print(result.is_exact)        # True

from pyeml import EMLRegressor

reg = EMLRegressor(max_depth=3, n_restarts=10)
reg.fit(x, y)

print(reg.expression)    # "exp(x)"
y_pred = reg.predict(x)  # exact predictions