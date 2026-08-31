def f(x):
    return x**3 - 2*x + 1

def analytical_derivative(x):
    return 3*x**2 - 2

def numerical_derivative(x, epsilon=1e-5):
    return (f(x + epsilon) - f(x - epsilon)) / (2 * epsilon)

for x in [-2, 0, 3]:
    num = numerical_derivative(x)
    ana = analytical_derivative(x)
    print(f"x={x}: numerical={num}, analytical={ana}, difference={abs(num - ana)}")