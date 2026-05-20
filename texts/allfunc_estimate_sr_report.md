# eml-sr All Function Estimation Report

**Total Equations Evaluated:** 100
**Successfully Recovered (RMSE < 1e-5):** 8
**Failed:** 92
**Total Time:** 177.24s

## Successes

| ID | Expected Formula | Found Formula | RMSE | Time (s) |
|---|---|---|---|---|
| I.12.1 | `mu*Nn` | `Times(v_{0}, v_{1})` | 0.00e+00 | 0.01 |
| I.12.5 | `q2*Ef` | `Times(v_{0}, v_{1})` | 0.00e+00 | 0.01 |
| I.14.3 | `m*g*z` | `Times(v_{1}, Times(v_{0}, v_{2}))` | 3.41e-15 | 0.18 |
| I.25.13 | `q/C` | `Divide(v_{0}, v_{1})` | 1.32e-16 | 0.03 |
| I.26.2 | `arcsin(n*sin(theta2))` | `ArcSin(Times(v_{0}, Sin(v_{1})))` | 3.41e-17 | 0.54 |
| I.29.4 | `omega/c` | `Divide(v_{0}, v_{1})` | 1.59e-16 | 0.03 |
| I.43.31 | `mob*kb*T` | `Times(v_{0}, Times(v_{1}, v_{2}))` | 3.72e-15 | 0.49 |
| II.27.18 | `epsilon*Ef**2` | `Times(v_{0}, Times(v_{1}, v_{1}))` | 0.00e+00 | 0.10 |

## Failures & Errors

| ID | Expected Formula | Found Formula | RMSE | Status | Time (s) |
|---|---|---|---|---|---|
| I.6.2a | `exp(-theta**2/2)/sqrt(2*pi)` | `Divide(Exp(Neg(v_{0})), ArcSin(v_{0}))` | 1.80e-02 | FAIL | 1.28 |
| I.6.2 | `exp(-(theta/sigma)**2/2)/(sqrt(2*pi)*sigma)` | `ArcTan(Divide(Cos(1), Neg(v_{1})))` | 2.34e-02 | FAIL | 1.31 |
| I.6.2b | `exp(-((theta-theta1)/sigma)**2/2)/(sqrt(2*pi)*sigma)` | `Tan(Divide(Inv(v_{0}), ArcSin(Pi)))` | 3.20e-02 | FAIL | 2.38 |
| I.8.14 | `sqrt((x2-x1)**2+(y2-y1)**2)` | `Plus(Log(v_{3}), Divide(v_{2}, v_{3}))` | 9.15e-01 | FAIL | 2.35 |
| I.9.18 | `G*m1*m2/((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)` | `EML(Divide(ArcTan(v_{0}), v_{5}), E)` | 1.01e-01 | FAIL | 4.04 |
| I.10.7 | `m_0/sqrt(1-v**2/c**2)` | `Plus(I, Plus(v_{0}, Inv(v_{2})))` | 8.34e-02 | FAIL | 1.07 |
| I.11.19 | `x1*y1+x2*y2+x3*y3` | `Plus(Exp(E), Times(v_{1}, v_{2}))` | 6.80e+00 | FAIL | 0.83 |
| I.12.2 | `q1*q2*r/(4*pi*epsilon*r**3)` | `Divide(Times(I, v_{0}), Log(v_{3}))` | 5.97e-02 | FAIL | 2.32 |
| I.12.4 | `q1*r/(4*pi*epsilon*r**3)` | `Divide(Divide(I, v_{2}), ArcTan(v_{1}))` | 9.64e-03 | FAIL | 2.86 |
| I.12.11 | `q*(Ef+B*v*sin(theta))` | `Times(v_{0}, Divide(Exp(E), v_{4}))` | 1.85e+01 | FAIL | 0.61 |
| I.13.4 | `1/2*m*(v**2+u**2+w**2)` | `Subtract(Times(v_{0}, Exp(E)), E)` | 1.72e+01 | FAIL | 0.47 |
| I.13.12 | `G*m1*m2*(1/r2-1/r1)` | `Times(v_{1}, Subtract(v_{2}, v_{3}))` | 7.25e+00 | FAIL | 0.58 |
| I.14.4 | `1/2*k_spring*x**2` | `Times(v_{0}, Sqrt(Exp(v_{1})))` | 2.13e+00 | FAIL | 0.35 |
| I.15.3x | `(x-u*t)/sqrt(1-u**2/c**2)` | `Subtract(Subtract(v_{0}, v_{3}), Log(v_{1}))` | 4.11e-01 | FAIL | 0.91 |
| I.15.3t | `(t-u*x/c**2)/sqrt(1-u**2/c**2)` | `Plus(I, Subtract(v_{3}, Inv(v_{1})))` | 1.01e-01 | FAIL | 1.57 |
| I.15.1 | `m_0*v/sqrt(1-v**2/c**2)` | `Times(v_{1}, Plus(v_{0}, Inv(v_{2})))` | 2.23e-01 | FAIL | 0.53 |
| I.16.6 | `(u+v)/(1+u*v/c**2)` | `Plus(0, Times(E, Log(v_{0})))` | 3.72e-01 | FAIL | 1.37 |
| I.18.4 | `(m1*r1+m2*r2)/(m1+m2)` | `Times(Sqrt(v_{2}), Sqrt(v_{3}))` | 2.53e-01 | FAIL | 1.82 |
| I.18.12 | `r*F*sin(theta)` | `FAILED (Data generation)` | N/A | FAIL_DATA | 0.00 |
| I.18.14 | `m*r*v*sin(theta)` | `FAILED (Data generation)` | N/A | FAIL_DATA | 0.00 |
| I.24.6 | `1/2*m*(omega**2+omega_0**2)*1/2*x**2` | `Times(v_{2}, EML(v_{3}, Sin(v_{0})))` | 6.24e+00 | FAIL | 0.57 |
| I.27.6 | `1/(1/d1+n/d2)` | `Divide(Divide(v_{1}, Pi), ArcTan(v_{2}))` | 1.72e-01 | FAIL | 2.52 |
| I.29.16 | `sqrt(x1**2+x2**2-2*x1*x2*cos(theta1-theta2))` | `Divide(Plus(v_{0}, v_{1}), Cos(I))` | 1.76e+00 | FAIL | 0.69 |
| I.30.3 | `Int_0*sin(n*theta/2)**2/sin(theta/2)**2` | `Times(Sqrt(v_{0}), Divide(v_{0}, v_{1}))` | 1.98e+00 | FAIL | 0.53 |
| I.30.5 | `arcsin(lambd/(n*d))` | `Times(v_{0}, Divide(Inv(v_{1}), v_{2}))` | 6.32e-03 | FAIL | 1.72 |
| I.32.5 | `q**2*a**2/(6*pi*epsilon*c**3)` | `ArcSin(Divide(v_{0}, Exp(v_{3})))` | 3.70e-01 | FAIL | 2.34 |
| I.32.17 | `(1/2*epsilon*c*Ef**2)*(8*pi*r**2/3)*(omega**4/(omega**2-omega_0**2)**2)` | `Plus(v_{2}, EML(v_{4}, Exp(v_{5})))` | 2.63e+00 | FAIL | 0.76 |
| I.34.8 | `q*v*B/p` | `Times(Sqrt(v_{1}), Plus(v_{0}, v_{2}))` | 4.51e+00 | FAIL | 0.52 |
| I.34.1 | `omega_0/(1-v/c)` | `Divide(Plus(v_{2}, v_{2}), ArcTan(v_{0}))` | 6.50e-01 | FAIL | 0.78 |
| I.34.14 | `(1+v/c)/sqrt(1-v**2/c**2)*omega_0` | `Divide(Exp(Sqrt(v_{2})), ArcTan(v_{0}))` | 4.65e-01 | FAIL | 1.07 |
| I.34.27 | `(h/(2*pi))*omega` | `Times(Log(v_{1}), Divide(v_{0}, Pi))` | 1.39e-01 | FAIL | 2.04 |
| I.37.4 | `I1+I2+2*sqrt(I1*I2)*cos(delta)` | `Plus(1, Plus(v_{0}, Cos(v_{2})))` | 2.44e+00 | FAIL | 0.50 |
| I.38.12 | `4*pi*epsilon*(h/(2*pi))**2/(m*q**2)` | `FAILED (Data generation)` | N/A | FAIL_DATA | 0.00 |
| I.39.1 | `3/2*pr*V` | `Times(Tan(1), Times(v_{0}, v_{1}))` | 1.59e-01 | FAIL | 0.45 |
| I.39.11 | `1/(gamma-1)*pr*V` | `Divide(Plus(v_{1}, v_{2}), Log(v_{0}))` | 1.69e+00 | FAIL | 0.51 |
| I.39.22 | `n*kb*T/V` | `Times(Log(v_{0}), Times(v_{1}, v_{3}))` | 5.04e+00 | FAIL | 0.56 |
| I.40.1 | `n_0*exp(-m*g*x/(kb*T))` | `EML(Divide(Log(v_{0}), v_{2}), v_{1})` | 4.42e-01 | FAIL | 6.72 |
| I.41.16 | `h/(2*pi)*omega**3/(pi**2*c**2*(exp((h/(2*pi))*omega/(kb*T))-1))` | `Times(Sqrt(v_{3}), Divide(v_{0}, v_{4}))` | 1.16e+00 | FAIL | 3.76 |
| I.43.16 | `mu_drift*q*Volt/d` | `Times(v_{1}, Divide(v_{2}, Log(v_{3})))` | 6.17e+00 | FAIL | 1.69 |
| I.43.43 | `1/(gamma-1)*kb*v/A` | `EML(Divide(v_{1}, v_{0}), v_{2})` | 1.03e+00 | FAIL | 2.99 |
| I.44.4 | `n*kb*T*ln(V2/V1)` | `Times(v_{0}, Times(v_{0}, Sin(v_{3})))` | 1.32e+01 | FAIL | 1.33 |
| I.47.23 | `sqrt(gamma*pr/rho)` | `Times(ArcTan(v_{1}), Exp(Inv(v_{2})))` | 3.84e-01 | FAIL | 4.35 |
| I.48.2 | `m*c**2/sqrt(1-v**2/c**2)` | `Times(v_{0}, Times(v_{2}, v_{2}))` | 3.65e+00 | FAIL | 0.48 |
| I.50.26 | `x1*(cos(omega*t)+alpha*cos(omega*t)**2)` | `Plus(I, Times(v_{1}, Log(v_{3})))` | 1.43e+00 | FAIL | 3.05 |
| II.2.42 | `kappa*(T2-T1)*A/d` | `Times(v_{3}, Subtract(v_{2}, v_{1}))` | 5.70e+00 | FAIL | 2.05 |
| II.3.24 | `Pwr/(4*pi*r**2)` | `Divide(Divide(Sin(E), v_{1}), v_{1})` | 2.33e-02 | FAIL | 10.01 |
| II.4.23 | `q/(4*pi*epsilon*r)` | `Divide(Divide(I, v_{2}), Sqrt(v_{1}))` | 2.41e-02 | FAIL | 19.95 |
| II.6.11 | `1/(4*pi*epsilon)*p_d*cos(theta)/r**2` | `Times(v_{1}, Divide(Cos(v_{2}), Pi))` | 1.18e-02 | FAIL | 22.56 |
| II.6.15a | `p_d/(4*pi*epsilon)*3*z/r**5*sqrt(x**2+y**2)` | `Times(ArcTan(v_{4}), ArcCos(ArcTan(v_{2})))` | 1.11e-01 | FAIL | 14.39 |
| II.6.15b | `p_d/(4*pi*epsilon)*3*cos(theta)*sin(theta)/r**3` | `Times(E, Divide(Cos(v_{2}), E))` | 2.14e-02 | FAIL | 1.91 |
| II.8.7 | `3/5*q**2/(4*pi*epsilon*d)` | `Divide(Times(I, Exp(v_{0})), v_{2})` | 5.48e-02 | FAIL | 1.16 |
| II.8.31 | `epsilon*Ef**2/2` | `Times(v_{0}, Sqrt(Exp(v_{1})))` | 2.11e+00 | FAIL | 0.19 |
| II.10.9 | `sigma_den/epsilon*1/(1+chi)` | `ArcTan(Times(v_{0}, Divide(E, v_{1})))` | 1.38e-01 | FAIL | 1.01 |
| II.11.3 | `q*Ef/(m*(omega_0**2-omega**2))` | `Divide(v_{0}, EML(I, ArcCos(v_{3})))` | 7.92e-02 | FAIL | 1.08 |
| II.11.17 | `n_0*(1+p_d*Ef*cos(theta)/(kb*T))` | `Plus(Cos(v_{4}), Exp(ArcSin(v_{3})))` | 1.18e+00 | FAIL | 0.81 |
| II.11.20 | `n_rho*p_d**2*Ef/(3*kb*T)` | `Times(v_{0}, Divide(v_{1}, v_{4}))` | 2.44e+00 | FAIL | 0.31 |
| II.11.27 | `n*alpha/(1-(n*alpha/3))*epsilon*Ef` | `Times(E, Times(v_{0}, v_{1}))` | 2.22e-01 | FAIL | 1.10 |
| II.11.28 | `1+n*alpha/(1-(n*alpha/3))` | `Divide(ArcTan(Exp(v_{0})), Cos(v_{1}))` | 1.44e-01 | FAIL | 1.02 |
| II.13.17 | `1/(4*pi*epsilon*c**2)*2*I/r` | `Divide(Tan(Divide(I, v_{1})), v_{1})` | 1.22e-02 | FAIL | 1.38 |
| II.13.23 | `rho_c_0/sqrt(1-v**2/c**2)` | `Plus(I, Plus(v_{0}, Inv(v_{2})))` | 8.48e-02 | FAIL | 0.73 |
| II.13.34 | `rho_c_0*v/sqrt(1-v**2/c**2)` | `Plus(Inv(v_{2}), Times(v_{0}, v_{1}))` | 1.83e-01 | FAIL | 0.29 |
| II.15.4 | `-mom*B*cos(theta)` | `Times(v_{0}, ArcTan(ArcCos(v_{2})))` | 4.35e+00 | FAIL | 0.25 |
| II.15.5 | `-p_d*Ef*cos(theta)` | `Exp(Times(Cos(v_{2}), Neg(E)))` | 3.56e+00 | FAIL | 0.26 |
| II.21.32 | `q/(4*pi*epsilon*r*(1-v/c))` | `Divide(Divide(I, v_{1}), ArcTan(v_{2}))` | 2.86e-02 | FAIL | 1.27 |
| II.24.17 | `sqrt(omega**2/c**2-pi**2/d**2)` | `Subtract(Divide(v_{0}, v_{1}), Inv(v_{0}))` | 8.68e-02 | FAIL | 0.83 |
| II.27.16 | `epsilon*c*Ef**2` | `Times(v_{1}, Exp(Exp(ArcTan(v_{2}))))` | 4.53e+01 | FAIL | 0.39 |
| II.34.2a | `q*v/(2*pi*r)` | `EML(Divide(Log(v_{0}), v_{2}), E)` | 2.30e-01 | FAIL | 1.93 |
| II.34.2 | `q*v*r/2` | `Times(Sqrt(v_{2}), Times(v_{0}, v_{1}))` | 3.04e+00 | FAIL | 0.42 |
| II.34.11 | `g_*q*B/(2*m)` | `Divide(Times(v_{0}, v_{1}), Sqrt(v_{3}))` | 3.11e+00 | FAIL | 0.43 |
| II.34.29a | `q*h/(4*pi*m)` | `Divide(Log(v_{0}), ArcSin(v_{2}))` | 1.38e-01 | FAIL | 2.24 |
| II.34.29b | `g_*mom*B*Jz/(h/(2*pi))` | `Times(v_{4}, Times(v_{3}, Exp(Pi)))` | 1.53e+02 | FAIL | 0.63 |
| II.35.18 | `n_0/(exp(mom*B/(kb*T))+exp(-mom*B/(kb*T)))` | `Divide(Divide(v_{0}, E), ArcTan(v_{3}))` | 2.42e-01 | FAIL | 2.54 |
| II.35.21 | `n_rho*mom*tanh(mom*B/(kb*T))` | `Subtract(Times(v_{0}, v_{1}), v_{4})` | 2.21e+00 | FAIL | 0.77 |
| II.36.38 | `mom*H/(kb*T)+(mom*alpha)/(epsilon*c**2*kb*T)*M` | `Times(Sqrt(v_{1}), Divide(v_{0}, v_{2}))` | 5.76e-01 | FAIL | 3.72 |
| II.37.1 | `mom*(1+chi)*B` | `Times(v_{2}, Times(v_{0}, v_{1}))` | 1.06e+01 | FAIL | 0.49 |
| II.38.3 | `Y*A*x/d` | `Times(Log(v_{1}), Times(v_{0}, v_{3}))` | 6.65e+00 | FAIL | 0.55 |
| II.38.14 | `Y/(2*(1+sigma))` | `Times(Log(v_{0}), ArcTan(Inv(v_{1})))` | 5.97e-02 | FAIL | 1.79 |
| III.4.32 | `1/(exp((h/(2*pi))*omega/(kb*T))-1)` | `Divide(Times(v_{2}, v_{3}), ArcTan(v_{1}))` | 4.94e+00 | FAIL | 0.62 |
| III.4.33 | `(h/(2*pi))*omega/(exp((h/(2*pi))*omega/(kb*T))-1)` | `Plus(Sin(E), Times(v_{2}, v_{3}))` | 3.81e-01 | FAIL | 0.55 |
| III.7.38 | `2*mom*B/(h/(2*pi))` | `Times(Exp(Pi), Divide(v_{1}, v_{2}))` | 3.14e+01 | FAIL | 0.44 |
| III.8.54 | `sin(E_n*t/(h/(2*pi)))**2` | `ArcSin(Divide(Cos(1), ArcTan(v_{2})))` | 3.22e-01 | FAIL | 1.23 |
| III.9.52 | `(p_d*Ef*t/(h/(2*pi)))*sin((omega-omega_0)*t/2)**2/((omega-omega_0)*t/2)**2` | `Plus(Exp(v_{0}), Times(Pi, v_{1}))` | 1.21e+01 | FAIL | 0.42 |
| III.10.19 | `mom*sqrt(Bx**2+By**2+Bz**2)` | `FAILED (Data generation)` | N/A | FAIL_DATA | 0.00 |
| III.12.43 | `n*(h/(2*pi))` | `Times(Log(v_{0}), Divide(v_{1}, E))` | 3.08e-01 | FAIL | 1.17 |
| III.13.18 | `2*E_n*d**2*k/(h/(2*pi))` | `Times(v_{0}, Times(v_{2}, Exp(v_{1})))` | 3.14e+02 | FAIL | 0.31 |
| III.14.14 | `I_0*(exp(q*Volt/(kb*T))-1)` | `Times(v_{2}, EML(v_{1}, ArcCos(v_{3})))` | 3.77e+00 | FAIL | 0.36 |
| III.15.12 | `2*U*(1-cos(k*d))` | `Plus(Sin(v_{2}), Plus(1, v_{0}))` | 3.73e+00 | FAIL | 0.27 |
| III.15.14 | `(h/(2*pi))**2/(2*E_n*d**2)` | `Times(Log(v_{0}), Divide(I, v_{2}))` | 6.35e-03 | FAIL | 1.91 |
| III.15.27 | `2*pi*alpha/(n*d)` | `Times(E, Divide(v_{0}, v_{1}))` | 1.55e+00 | FAIL | 0.48 |
| III.17.37 | `beta*(1+alpha*cos(theta))` | `Times(E, Times(v_{1}, Cos(v_{2})))` | 3.41e+00 | FAIL | 0.74 |
| III.19.51 | `-m*q**4/(2*(4*pi*epsilon)**2*(h/(2*pi))**2)*(1/n**2)` | `FAILED (Data generation)` | N/A | FAIL_DATA | 0.00 |
| III.21.20 | `-rho_c_0*q*A_vec/m` | `Subtract(Times(v_{0}, Neg(v_{2})), v_{1})` | 8.79e+00 | FAIL | 1.60 |