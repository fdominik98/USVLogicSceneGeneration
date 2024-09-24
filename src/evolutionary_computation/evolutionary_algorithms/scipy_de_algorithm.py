from scipy.optimize import differential_evolution

# Define your objectives
def objective(x, weights=[0.5, 0.5]):
    f1 = x[0]**2 + x[1]**2
    f2 = (x[0] - 2)**2 + (x[1] - 1)**2
    return weights[0] * f1 + weights[1] * f2

bounds = [(-5, 5), (-5, 5)]

# Use different weight combinations for different Pareto solutions
result = differential_evolution(objective, bounds, args=([0.7, 0.3],))
print(result)