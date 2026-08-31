def loss(w):
    return 0.5 * (w - 4)**2

def grad(w):
    return w - 4

def minimize_quadratic(initial, learning_rate=0.1, steps=10):
    if learning_rate <= 0:
        raise ValueError("Learning rate must be positive.")
    if steps <= 0:
        raise ValueError("Number of steps must be positive.")

    w = float(initial)
    history = []
    for step in range(steps+1):
        history.append((step, w, loss(w)))
        if step < steps:  # Avoid computing gradient on the last step
            w = w - learning_rate * grad(w)
    return history

for lr in [0.1, 1.0, 1.9, 2.1]:
    hist = minimize_quadratic(initial=0, learning_rate=lr, steps=10)
    print(f"Learning rate: {lr}, last = {hist[-1]}")