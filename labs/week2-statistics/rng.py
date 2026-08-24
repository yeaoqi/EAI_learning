import numpy as np

def run_once(seed, true_p=0.7, n=100):
    rng = np.random.default_rng(seed)
    return (rng.random(n) < true_p).mean()

seeds = range(10)
results = np.array([run_once(seed) for seed in seeds])

print("results:", results)
print("mean:", results.mean())
print("sample std:", results.std(ddof=1))
print("min:", results.min())
print("max:", results.max())
print("best - mean:", results.max() - results.mean())