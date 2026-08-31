import numpy as np

def forward(params, x, y):
    W1, b1, W2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]
    z = W1 @ x + b1
    h = np.maximum(0.0, z)
    o = W2 @ h + b2
    diff = o - y
    loss = 0.5 * float((diff.T @ diff).item())
    cache = {"x": x, "y": y, "z": z, "h": h, "o": o, "diff": diff}
    return loss, cache

def backward(params, cache):
    x, z, h, diff = cache["x"], cache["z"], cache["h"], cache["diff"]
    W2 = params["W2"]

    do = diff
    dW2 = do @ h.T
    db2 = do
    dh = W2.T @ do
    dz = dh * (z > 0.0)
    dW1 = dz @ x.T
    db1 = dz

    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}

def numerical_grads(params, x, y, epsilon=1e-5):
    grads = {}
    for name, value in params.items():
        grad = np.zeros_like(value)
        it = np.nditer(value, flags=['multi_index'], op_flags=['readwrite'])
        while not it.finished:
            idx = it.multi_index
            old = value[idx]
            
            value[idx] = old + epsilon
            loss_plus, _ = forward(params, x, y)

            value[idx] = old - epsilon
            loss_minus, _ = forward(params, x, y)

            value[idx] = old
            grad[idx] = (loss_plus - loss_minus) / (2 * epsilon)
            it.iternext()

        grads[name] = grad
    return grads

rng = np.random.default_rng(2)
d, k, c = 3, 4, 2
params = {
    "W1": rng.normal(0, 0.2, size=(k, d)),
    "b1": rng.normal(0, 0.2, size=(k, 1)),
    "W2": rng.normal(0, 0.2, size=(c, k)),
    "b2": rng.normal(0, 0.2, size=(c, 1))
}

x = rng.normal(0, 1, size=(d, 1))
y = rng.normal(0, 1, size=(c, 1))

# 人为构造一个接近ReLu拐点隐藏单元
params["b1"][0, 0] = -float((params["W1"][0:1] @ x).item()) + 1e-4

loss_value, cache = forward(params, x, y)
analytic = backward(params, cache)
numeric = numerical_grads(params, x, y)

max_error = 0.0
for name in params:
    error = np.max(np.abs(analytic[name] - numeric[name]))
    max_error = max(max_error, float(error))
    print(name, error)

print("loss:", loss_value)
print("max error:", max_error)
