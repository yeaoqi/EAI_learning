import numpy as np
from scipy import stats

def ci_t(values, confidence=0.95):
    x = np.array(values)
    n = x.size
    mean = x.mean()
    se = x.std(ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf(1 - (1 - confidence) / 2, df=n-1)
    return mean - t_crit * se, mean + t_crit * se

def coverage_simulation(n, repeats=1000, true_mu=0.0, true_sigma=1.0, seed=42):
    rng = np.random.default_rng(seed)
    covered = 0
    for _ in range(repeats):
        sample = rng.normal(true_mu, true_sigma, size=n)
        low, high = ci_t(sample)
        covered += int(low <= true_mu <= high)
    return covered / repeats

for n in [5, 20, 100]:
    print(n, coverage_simulation(n))

