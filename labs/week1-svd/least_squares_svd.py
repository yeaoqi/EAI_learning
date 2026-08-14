import numpy as np

np.random.seed(42)


def add_noise(x):
    noise = np.random.normal(0, 0.1, x.shape)
    return 2 * x + 1 + noise


def design_matrix(x):
    return np.vstack([x, np.ones_like(x)]).T


def solve_and_report(name, x, y):
    A = design_matrix(x)
    theta_lstsq, residuals, rank, singular_values = np.linalg.lstsq(
        A, y, rcond=None
    )

    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    theta_svd = Vt.T @ np.diag(1 / s) @ U.T @ y
    condition_number = s[0] / s[-1]

    print(f"\n[{name}]")
    print(f"theta_lstsq = {theta_lstsq}")
    print(f"theta_svd   = {theta_svd}")
    print(f"residuals   = {residuals}")
    print(f"rank        = {rank}")
    print(f"singular values = {singular_values}")
    print(f"condition number = {condition_number}")
    print(f"difference between methods = {np.linalg.norm(theta_lstsq - theta_svd)}")


x = np.random.uniform(-1, 1, 100)
y = add_noise(x)
solve_and_report("normal data", x, y)

xs = np.linspace(1, 1.0000001, 20)
ys = add_noise(xs)
solve_and_report("ill-conditioned data", xs, ys)
