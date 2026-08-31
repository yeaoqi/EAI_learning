import numpy as np

def simulate_success_rate(p, n, seed):
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1]")
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

    rng = np.random.default_rng(seed)
    trials = rng.random(n) < p
    return trials.mean()

for n in [10, 100, 10000]:
    print(n, simulate_success_rate(p=0.7, n=n, seed=42))