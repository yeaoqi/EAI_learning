import numpy as np
import matplotlib.pyplot as plt

class Adam:
    def __init__(self, shape, learning_rate=0.01, beta1=0.9, beta2=0.999, epsilon=1e-8):
        if learning_rate <= 0:
            raise ValueError("Learning rate must be positive.")
        if not (0 <= beta1 < 1):
            raise ValueError("Beta1 must be in the range [0, 1).")
        if not (0 <= beta2 < 1):
            raise ValueError("Beta2 must be in the range [0, 1).")
        if epsilon <= 0:
            raise ValueError("Epsilon must be positive.")

        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = np.zeros(shape, dtype=float)
        self.v = np.zeros(shape, dtype=float)
        self.t = 0

    def step(self, weights, gradients):
        gradients = np.array(gradients, dtype=float)
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradients
        self.v = self.beta2 * self.v + (1 - self.beta2) * gradients ** 2
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        return weights - self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)

def quadratic_loss(w):
    return 0.5 * (w - 4) ** 2

def quadratic_grad(w):
    return w - 4

def run_sgd(lr, steps=200, threshold=1e-8):
    w = np.array([0.0])
    losses = []
    reached = None
    for step in range(steps):
        current_loss = float(quadratic_loss(w)[0])
        losses.append(current_loss)
        if reached is None and current_loss <= threshold:
            reached = step
        w = w - lr * quadratic_grad(w)
    return np.array(losses), reached

def run_adam(lr, steps=200, threshold=1e-8):
    w = np.array([0.0])
    opt = Adam(w.shape, learning_rate=lr)
    losses = []
    reached = None
    for step in range(steps):
        current_loss = float(quadratic_loss(w)[0])
        losses.append(current_loss)
        if reached is None and current_loss <= threshold:
            reached = step
        w = opt.step(w, quadratic_grad(w))
    return np.array(losses), reached

for lr in [0.01, 0.1, 0.5]:
    sgd_losses, sgd_reached = run_sgd(lr)
    adam_losses, adam_reached = run_adam(lr)
    print(
        f"Learning Rate: {lr}, "
        f"SGD reached threshold at step: {sgd_reached}, final loss: {sgd_losses[-1]:.6f}, "
        f"Adam reached threshold at step: {adam_reached}, final loss: {adam_losses[-1]:.6f}"
    )
    plt.plot(sgd_losses, label=f"SGD lr={lr}")
    plt.plot(adam_losses, label=f"Adam lr={lr}")


plt.yscale("log")    
plt.xlabel("Step")
plt.ylabel("Loss")
plt.legend()
plt.show()
