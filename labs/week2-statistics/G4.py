import numpy as np

def sample_statistics(values):
    """返回样本均值、无偏样本方差和样本标准差"""
    x = np.asarray(values, dtype=float)
    n = x.size
    if n < 2:
        raise ValueError("at least two values are required")

    mean = x.sum() / n
    centered = x - mean
    var = np.sum(centered ** 2) / (n - 1)
    std = np.sqrt(var)
    return mean, var, std

values = np.array([0.72, 0.81, 0.76, 0.85, 0.79])
mean, var, std = sample_statistics(values)

print(mean, np.mean(values))
print(var, np.var(values, ddof=1))
print(std, np.std(values, ddof=1))
