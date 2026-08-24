import numpy as np

def coin_estimates(true_p=0.7, ns=(5, 20, 100, 1000), priors=((1, 1), (2, 2), (8, 2)), seed=42):
    rng = np.random.default_rng(seed)
    rows = []

    for n in ns:
        data = rng.random(n) < true_p
        k = int(data.sum())
        mle = k / n

        row = {"n": n, "k": k, "true_p": true_p, "MLE": mle}
        for alpha, beta in priors:
            alpha_post = alpha + k
            beta_post = beta + n - k
            if alpha_post > 1 and beta_post > 1:
                map_estimate = (alpha_post - 1) / (alpha_post + beta_post - 2)
            else:
                map_estimate = 0.0 if alpha_post <=1 else 1.0
            row[f"map_beta_{alpha}_{beta}"] = map_estimate
        rows.append(row)

    return rows

for rows in coin_estimates():
    print(rows)
