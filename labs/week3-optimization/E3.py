import numpy as np
import matplotlib.pyplot as plt

def fit_linear_gd(X, y, learning_rate=0.05, steps=100):
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

    n, d = X.shape
    w = np.zeros((d, 1))
    losses = []

    for _ in range(steps):
        residual = X @ w - y
        loss_value = float(((residual.T @ residual) / (2 * n)).item())
        losses.append(loss_value)
        gradient = (X.T @ residual) / n
        w -= learning_rate * gradient

    return w, np.array(losses)

rng = np.random.default_rng(0)
n = 80
xs = rng.uniform(-3, 3, size=n)
noise = rng.normal(0, 0.5, size=n)
ys = 2.5 * xs + 1.0 + noise

X = np.column_stack([xs, np.ones_like(xs)])
y = ys.reshape(-1, 1)

for lr in [0.01, 0.05, 0.2]:
    w, losses = fit_linear_gd(X, y, learning_rate=lr, steps=300)
    print(f"Learning rate: {lr}, final weights: {w.ravel()}, final loss: {losses[-1]}")
    plt.plot(losses, label=f"lr={lr}")

plt.xlabel("Steps")
plt.ylabel("Loss")
plt.legend()
plt.show()
