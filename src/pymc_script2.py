import pymc as pm
import numpy as np

# Define the model with variables and constraints
with pm.Model() as model:
    # Define priors for each variable
    x1 = pm.Uniform('x1', lower=-10, upper=10)
    x2 = pm.Uniform('x2', lower=-10, upper=10)
    x3 = pm.Uniform('x3', lower=-10, upper=10)
    x4 = pm.Uniform('x4', lower=-10, upper=10)
    x5 = pm.Uniform('x5', lower=-10, upper=10)
    x6 = pm.Uniform('x6', lower=-10, upper=10)
    x7 = pm.Uniform('x7', lower=-10, upper=10)
    x8 = pm.Uniform('x8', lower=-10, upper=10)

    # Define the constraints with associated weights (potentials)
    constraints = [
        (x1 + x2 + x3 - 5, 1.0),  # Constraint with a weight of 1.0
        (x4 * x5 - 10, 2.0),       # Constraint with a weight of 2.0
        (x6 / x7 - 1, 1.5),        # Constraint with a weight of 1.5
        (x8 - x1**2, 2.5),         # Constraint with a weight of 2.5
        (x2 + x4 - x6, 1.0),       # Constraint with a weight of 1.0
        (x3 * x5 - x7, 1.2)        # Constraint with a weight of 1.2
    ]

    # Apply potentials for each constraint
    for i, (constraint, weight) in enumerate(constraints):
        pm.Potential(f'constraint_{i}', weight * pm.math.switch(pm.math.le(constraint, 0), 0, -np.inf))

# Sample from the model
with model:
    trace = pm.sample(1000, tune=1000, chains=2, cores=1, return_inferencedata=False)

# Extract samples
samples = trace.get_values(['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8'])