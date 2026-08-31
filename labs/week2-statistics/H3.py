import numpy as np
from scipy import stats

def mean_confidence_interval(values, confidence=0.95):
    """返回样本均值、置信区间下界和上界"""
    x = np.asarray(values, dtype=float)
    n = x.size
    if n < 2:
        raise ValueError("at least two values are required")

    mean = x.mean()
    s = x.std(ddof=1)
    se = s / np.sqrt(n)
    alpha = 1 - confidence
    t_crit = stats.t.ppf(1 - alpha /2, df=n-1)
    margin = t_crit * se
    return mean, mean - margin, mean + margin
