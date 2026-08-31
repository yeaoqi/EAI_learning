import numpy as np

def fit_linear_gd_l2(X, y, learning_rate=0.05, steps=100, lambda_=0.0):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    if X.ndim != 2:
        raise ValueError("X must be a 2D array.")
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    if y.ndim != 2 or y.shape[1] != 1:
        raise ValueError("y must have shape (n,) or (n, 1).")
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of rows.")
    if learning_rate <= 0:
        raise ValueError("Learning rate must be positive.")
    if steps <= 0:
        raise ValueError("Number of steps must be positive.")
    if lambda_ < 0:
        raise ValueError("Regularization parameter lambda_ must be non-negative.")

    n, d = X.shape
    w = np.zeros((d, 1))
    losses = []

    for _ in range(steps):
        residual = X @ w - y
        weights_without_bias = w.copy()
        weights_without_bias[-1, 0] = 0

        data_loss = float(((residual.T @ residual) / (2 * n)).item())
        reg_loss = float((lambda_ / 2 * np.sum(weights_without_bias ** 2)).item())
        losses.append(data_loss + reg_loss)

        gradient = (X.T @ residual) / n + lambda_ * weights_without_bias
        w -= learning_rate * gradient

    return w, np.array(losses)

def mse(X, y, w):
    residual = X @ w - y
    return float(np.mean(residual ** 2))

rng = np.random.default_rng(1)
n = 120
xs = rng.uniform(-3, 3, size=n)
ys = 2.5 * xs + 1.0 + rng.normal(0, 0.8, size=n)
X = np.column_stack([xs, np.ones_like(xs)])
y = ys.reshape(-1, 1)

idx = rng.permutation(n)
train_idx, val_idx = idx[:90], idx[90:]
X_train, y_train = X[train_idx], y[train_idx]
X_val, y_val = X[val_idx], y[val_idx]
    
for lambda_ in [0.0, 0.01, 0.2]:
    w, losses = fit_linear_gd_l2(
        X_train, y_train, learning_rate=0.05, steps=1000, lambda_=lambda_
    )
    weight_norm = float(np.linalg.norm(w[:-1]))
    val_mse = mse(X_val, y_val, w)
    print(f"Lambda: {lambda_}, weight norm: {weight_norm}, val MSE: {val_mse}")
