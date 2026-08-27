# 03 微积分与优化自测

本文件用于第三周学习与自测。建议先独立作答；不确定的地方标记为“待补充”，完成代码实验后再回来修改。

## A. 导数与微分

### A1. 导数的直观含义

请分别从几何和数值变化率的角度解释导数。为什么导数可以用于预测函数在小范围内的变化？

答案：

从几何上看，导数是函数图像在某一点处切线的斜率。斜率为正，函数在该点附近上升；斜率为负，函数在该点附近下降；斜率绝对值越大，变化越陡。

从数值变化率看，导数描述输入发生一个很小变化时，输出大约变化多少：

```text
f'(x) = lim_{h->0} [f(x+h)-f(x)] / h
```

当 `h` 足够小时，函数在局部可以用切线近似：

```text
f(x+h) ≈ f(x) + f'(x)h
```

所以导数可以预测函数在小范围内的变化，这也是梯度下降用梯度决定参数更新方向的基础。

### A2. 基本求导

求下列函数的导数，并写出使用的规则：

1. `f(x)=3x^4-2x+7`
2. `g(x)=e^x ln(x)`（`x>0`）
3. `h(x)=(x^2+1)^3`

答案：

1. `f'(x)=12x^3-2`。使用幂函数求导、常数倍法则、和差法则，常数项导数为 `0`。
2. `g'(x)=e^x ln(x)+e^x/x = e^x(ln(x)+1/x)`。使用乘积法则，`(e^x)'=e^x`，`(ln x)'=1/x`。
3. `h'(x)=3(x^2+1)^2 * 2x = 6x(x^2+1)^2`。使用链式法则。

### A3. 链式法则

设 `y=sin(x^2+1)`，请逐步推导 `dy/dx`。在神经网络中，链式法则对应哪一步计算？

答案：

令：

```text
u = x^2 + 1
y = sin(u)
```

则：

```text
dy/du = cos(u)
du/dx = 2x
dy/dx = dy/du * du/dx = cos(x^2+1) * 2x
```

所以：

```text
dy/dx = 2x cos(x^2+1)
```

在神经网络中，链式法则对应反向传播：从损失函数开始，把上游梯度逐层乘以当前层的局部导数，得到每个参数对损失的影响。

### A4. 有限差分

为什么可以用 `(f(x+ε)-f(x-ε))/(2ε)` 近似导数？当 `ε` 太大或太小时分别会有什么问题？

答案：

中心有限差分用 `x` 两侧的函数值估计局部斜率：

```text
f'(x) ≈ [f(x+ε)-f(x-ε)] / (2ε)
```

它比单边差分更准确，因为一阶误差项会部分抵消，主要截断误差通常是 `O(ε^2)`。

`ε` 太大时，计算的是较大区间上的平均斜率，不能很好代表 `x` 附近的局部导数。`ε` 太小时，`f(x+ε)` 和 `f(x-ε)` 非常接近，浮点数相减会产生明显舍入误差，导致结果不稳定。

## B. 多元函数与梯度

### B1. 偏导数与梯度

对 `f(x,y)=x^2+3xy+2y^2` 求梯度和 Hessian 矩阵，并计算点 `(1,-1)` 处的梯度。

答案：

偏导数为：

```text
∂f/∂x = 2x + 3y
∂f/∂y = 3x + 4y
```

所以梯度为：

```text
∇f(x,y) = [2x+3y, 3x+4y]^T
```

Hessian 矩阵为：

```text
H = [[2, 3],
     [3, 4]]
```

在 `(1,-1)` 处：

```text
∇f(1,-1) = [2*1+3*(-1), 3*1+4*(-1)]^T = [-1, -1]^T
```

### B2. 梯度方向

为什么 `∇f(x)` 指向局部增长最快的方向？为什么梯度下降要沿 `-∇f(x)` 更新？

答案：

任意单位方向 `u` 上的方向导数为：

```text
D_u f(x) = ∇f(x)^T u
```

根据 Cauchy-Schwarz 不等式：

```text
∇f(x)^T u <= ||∇f(x)|| ||u||
```

当 `u` 与 `∇f(x)` 同方向时，方向导数最大。因此梯度方向是局部增长最快的方向。

如果目标是最小化函数，就要让函数值下降最快，所以沿负梯度方向更新：

```text
x_{t+1} = x_t - η∇f(x_t)
```

### B3. 极值与 Hessian

利用 Hessian 判断 `f(x,y)=x^2+3xy+2y^2` 在原点是局部极小、局部极大还是鞍点。说明仅凭 `∇f=0` 为什么不能完成判断。

答案：

原点处：

```text
∇f(0,0) = [0,0]^T
```

Hessian 为：

```text
H = [[2, 3],
     [3, 4]]
```

判断二阶主子式：

```text
det(H) = 2*4 - 3*3 = -1 < 0
```

Hessian 不定，说明函数在原点附近有的方向向上弯，有的方向向下弯，所以原点是鞍点。

仅凭 `∇f=0` 只能说明一阶变化为零，也就是驻点；驻点可能是局部极小、局部极大或鞍点，需要二阶信息或其他全局信息进一步判断。

### B4. 凸函数

什么是凸函数？为什么凸优化问题中任意局部最小值都是全局最小值？请举一个机器学习中的凸优化例子。

答案：

函数 `f` 是凸函数，指对任意 `x,y` 和 `t∈[0,1]`，都有：

```text
f(tx+(1-t)y) <= t f(x) + (1-t) f(y)
```

直观上，函数图像任意两点之间的连线都在图像上方或贴着图像。凸函数没有“隐藏的低谷”。如果某个点是局部最小值，但不是全局最小值，那么它和更低点之间的连线会产生一个继续下降的方向，这与局部最小矛盾。因此凸优化中任意局部最小值都是全局最小值。

机器学习例子：普通线性回归的平方损失是关于参数的凸函数；带 L2 正则化的线性回归也是凸优化问题。

### B5. Jacobian 矩阵

设向量函数 `f(x,y)=[x²+y, sin(xy)]^T`。请写出它的 Jacobian 矩阵，并说明 Jacobian 与梯度的区别。

答案：

令：

```text
f1(x,y) = x^2 + y
f2(x,y) = sin(xy)
```

Jacobian 矩阵是每个输出对每个输入的偏导：

```text
J_f(x,y) =
[[∂f1/∂x, ∂f1/∂y],
 [∂f2/∂x, ∂f2/∂y]]
=
[[2x, 1],
 [y cos(xy), x cos(xy)]]
```

梯度通常针对标量函数 `f: R^n -> R`，结果是一个向量；Jacobian 针对向量函数 `f: R^n -> R^m`，结果是一个 `m x n` 矩阵。标量函数的梯度可以看作 Jacobian 的特殊情况。

## C. 梯度下降

### C1. 更新规则

写出梯度下降的参数更新公式，并解释参数、学习率、梯度和停止条件各自的作用。学习率过大或过小时，损失曲线通常是什么样子？

答案：

梯度下降更新公式为：

```text
θ_{t+1} = θ_t - η∇J(θ_t)
```

其中：

- `θ` 是待优化参数。
- `η` 是学习率，控制每次更新步长。
- `∇J(θ_t)` 是当前参数处损失函数的梯度，指出损失增长最快方向。
- 停止条件可以是达到最大步数、损失下降很小、梯度范数很小、验证集不再提升等。

学习率过大时，损失曲线常表现为上下震荡、不能稳定下降，甚至直接发散变成越来越大。学习率过小时，损失曲线下降很慢，看起来长时间近似平坦，需要很多步才能接近最优点。

### C2. 一元函数手算

对 `J(w)=(w-3)^2` 从 `w_0=0` 开始，取学习率 `η=0.1`，手算前 3 次更新，并说明最终会趋向哪里。

答案：

先求梯度：

```text
J'(w)=2(w-3)
```

更新规则：

```text
w_{t+1}=w_t-0.1*2(w_t-3)=w_t-0.2(w_t-3)
```

前 3 次更新：

```text
w0 = 0
J'(w0) = -6
w1 = 0 - 0.1*(-6) = 0.6

J'(w1) = 2*(0.6-3) = -4.8
w2 = 0.6 - 0.1*(-4.8) = 1.08

J'(w2) = 2*(1.08-3) = -3.84
w3 = 1.08 - 0.1*(-3.84) = 1.464
```

最终会趋向最小点 `w=3`，此时 `J(w)=0`。

### C3. 线性回归梯度推导

给定 `J(w)=1/(2n)||Xw-y||²`：

1. 推导 `∇J(w)`；
2. 标出每个矩阵的形状；
3. 解释为什么偏置可以通过给 `X` 增加一列全 1 表示。

答案：

设：

```text
r = Xw - y
J(w) = (1/(2n)) r^T r
```

对 `w` 求导：

```text
∇J(w) = (1/n) X^T(Xw-y)
```

矩阵形状：

```text
X: n x d
w: d x 1
y: n x 1
Xw: n x 1
r = Xw-y: n x 1
X^T: d x n
∇J(w): d x 1
```

如果模型是：

```text
ŷ = Xw + b
```

可以给 `X` 增加一列全 `1`，并把 `b` 放进参数向量：

```text
X_aug = [X, 1]
w_aug = [w, b]^T
ŷ = X_aug w_aug
```

这样偏置项就变成了普通权重，梯度推导和代码实现都更统一。

### C4. 批量与随机梯度下降

比较批量梯度下降、SGD 和小批量梯度下降的每步数据量、梯度噪声、计算成本和适用场景。

答案：

批量梯度下降每一步使用全部训练数据，梯度最稳定、噪声最小，但单步计算成本高，数据很大时更新慢。它适合数据量较小、希望损失稳定下降的场景。

SGD 每一步只使用一个样本，单步成本最低，更新频繁，但梯度噪声很大，损失曲线会明显抖动。它适合超大规模数据或在线学习，但通常需要学习率衰减。

小批量梯度下降每一步使用一小批样本，例如 `32`、`64`、`256` 个。它在梯度稳定性和计算效率之间折中，能利用矩阵运算和 GPU 并行，是深度学习中最常用的训练方式。

### C5. Adam 优化器

请写出 Adam 中一阶矩 `m_t`、二阶矩 `v_t`、偏差修正和参数更新公式。它相比普通 SGD 解决了哪些问题？学习率、`beta1`、`beta2` 和 `epsilon` 分别有什么作用？

答案：

给定当前梯度 `g_t = ∇J(θ_t)`，Adam 的更新为：

```text
m_t = beta1 * m_{t-1} + (1-beta1) * g_t
v_t = beta2 * v_{t-1} + (1-beta2) * g_t^2

m_hat_t = m_t / (1 - beta1^t)
v_hat_t = v_t / (1 - beta2^t)

θ_{t+1} = θ_t - η * m_hat_t / (sqrt(v_hat_t) + epsilon)
```

其中 `g_t^2` 是逐元素平方。Adam 相比普通 SGD 同时引入了动量和自适应步长：一阶矩让更新方向更平滑，二阶矩让不同参数按梯度尺度自动调整步长。它常能缓解普通 SGD 对学习率敏感、不同参数尺度差异大、梯度噪声较强等问题。

参数作用：

- `η`：全局学习率，控制整体更新幅度。
- `beta1`：一阶矩衰减系数，越大越强调历史方向，常用 `0.9`。
- `beta2`：二阶矩衰减系数，越大越平滑梯度平方估计，常用 `0.999`。
- `epsilon`：防止除以零，并提升数值稳定性。

### C6. 两层网络反向传播

考虑 `z=W1x+b1`、`h=ReLU(z)`、`o=W2h+b2` 和平方损失 `L=1/2||o-y||²`。请从 `∂L/∂o` 开始，逐层推导 `W2`、`b2`、`W1` 和 `b1` 的梯度，并标出每个张量的形状。

答案：

设输入维度为 `d`，隐藏层维度为 `k`，输出维度为 `c`：

```text
x: d x 1
W1: k x d
b1: k x 1
z: k x 1
h: k x 1
W2: c x k
b2: c x 1
o: c x 1
y: c x 1
```

平方损失：

```text
L = 1/2 ||o-y||^2
```

从输出层开始：

```text
δo = ∂L/∂o = o - y                 # c x 1
∂L/∂W2 = δo h^T                    # c x k
∂L/∂b2 = δo                        # c x 1
```

传回隐藏层：

```text
∂L/∂h = W2^T δo                    # k x 1
ReLU'(z) = 1(z > 0)                # k x 1
δz = (W2^T δo) ⊙ 1(z > 0)          # k x 1
```

第一层参数梯度：

```text
∂L/∂W1 = δz x^T                    # k x d
∂L/∂b1 = δz                        # k x 1
```

如果是批量输入，通常把样本维度放在矩阵中，再对 batch 维度求和或取平均。

## D. 正则化与数值稳定性

### D1. L1 与 L2 正则化

分别写出 L1、L2 正则化目标函数及其直观作用。为什么 L1 更容易产生零参数？`λ` 过大可能导致什么问题？

答案：

L1 正则化：

```text
J_reg(w) = J(w) + λ||w||_1 = J(w) + λ sum_i |w_i|
```

L2 正则化：

```text
J_reg(w) = J(w) + (λ/2)||w||_2^2 = J(w) + (λ/2) sum_i w_i^2
```

L1 的直观作用是鼓励稀疏参数，让不重要的特征权重变成 `0`，可用于特征选择。L2 的直观作用是惩罚过大的权重，让参数更平滑、更小，减少模型对单个特征或噪声的过度依赖。

L1 更容易产生零参数，是因为 `|w|` 在 `0` 处有尖点，优化时会把小权重直接压到 `0`。L2 的梯度与 `w` 成正比，权重越接近 `0`，惩罚梯度越小，所以通常让权重变小但不一定精确为 `0`。

`λ` 过大会让正则化项压过数据损失，模型参数被过度压缩，容易欠拟合，训练集和验证集表现都变差。

### D2. 特征缩放

当两个特征的数值范围相差很大时，梯度下降为什么容易震荡或收敛缓慢？标准化如何改善这个问题？

答案：

特征尺度差异很大时，损失函数的等高线会变得很狭长。梯度下降在大尺度特征方向上可能迈得太大，在小尺度特征方向上又迈得太小，于是参数更新容易来回震荡，并且沿狭长谷底缓慢前进。

标准化通常把每个特征变成均值约为 `0`、标准差约为 `1`：

```text
x' = (x - mean) / std
```

这样不同特征的尺度更接近，损失曲面的条件数通常更好，梯度下降可以使用更统一的学习率，收敛更快、更稳定。

### D3. 训练、验证与测试

为什么不能使用测试集选择学习率或正则化系数？训练损失下降而验证损失上升说明什么？

答案：

测试集应该只在最终评估时使用，用来估计模型在未知数据上的泛化能力。如果用测试集反复选择学习率、正则化系数或模型结构，测试集信息就会泄漏进训练流程，最终测试结果会偏乐观，不能代表真实泛化性能。

训练损失下降而验证损失上升，通常说明模型正在过拟合：它越来越适应训练集细节甚至噪声，但对未见数据的表现变差。可考虑更强正则化、早停、数据增强、减少模型容量或增加训练数据。

### D4. 梯度爆炸与梯度消失

什么是梯度爆炸和梯度消失？它们在深层网络或长链式计算中为什么会出现？请列出至少两种诊断信号和两种缓解方法。

答案：

梯度爆炸是反向传播过程中梯度范数变得非常大，导致参数更新剧烈、损失不稳定甚至出现 `NaN`。梯度消失是梯度在向前层传播时变得非常小，导致前面层几乎学不到东西。

它们出现的原因是链式法则会连续相乘很多局部导数或权重矩阵。如果这些因子的尺度长期大于 `1`，梯度容易指数级放大；如果长期小于 `1`，梯度容易指数级衰减。

诊断信号：

- 梯度范数异常大、异常小，或不同层梯度差异极大。
- 损失突然发散、出现 `inf/NaN`，或长时间几乎不下降。
- 前面层参数更新量接近 `0`，激活值大量饱和。

缓解方法：

- 梯度裁剪，限制梯度范数。
- 合理初始化，例如 Xavier/He 初始化。
- 使用归一化层，例如 BatchNorm 或 LayerNorm。
- 使用残差连接、合适激活函数、较小学习率或学习率调度。

### D5. Lagrange 乘子

使用 Lagrange 乘子求解：在约束 `x²+y²=1` 下最小化 `f(x,y)=x+y`。写出 Lagrangian、一阶条件，并解释约束梯度与目标梯度的几何关系。

答案：

约束写成：

```text
g(x,y) = x^2 + y^2 - 1 = 0
```

Lagrangian：

```text
L(x,y,λ) = x + y + λ(x^2+y^2-1)
```

一阶条件：

```text
∂L/∂x = 1 + 2λx = 0
∂L/∂y = 1 + 2λy = 0
∂L/∂λ = x^2 + y^2 - 1 = 0
```

由前两式可得 `x=y`。代入约束：

```text
2x^2 = 1
x = y = ±1/sqrt(2)
```

目标函数值：

```text
x+y = sqrt(2)      when x=y=1/sqrt(2)
x+y = -sqrt(2)     when x=y=-1/sqrt(2)
```

所以最小值在：

```text
(x,y)=(-1/sqrt(2), -1/sqrt(2))
最小值 = -sqrt(2)
```

几何上，在约束曲线上的最优点，目标函数的等高线与约束曲线相切，因此目标梯度与约束梯度平行：

```text
∇f = -λ∇g
```

具体符号取决于 Lagrangian 的写法。

### D6. 欠拟合与优化不收敛

如何区分“模型表达能力不足导致的欠拟合”和“优化过程没有收敛”？请根据训练/验证损失曲线、梯度范数和参数更新提出一个排查顺序。

答案：

欠拟合通常表现为训练损失和验证损失都比较高，并且二者差距不大；即使训练充分，模型也无法把训练集拟合好。优化不收敛则更强调训练过程本身没有稳定到一个好解，例如损失震荡、发散、下降很慢或卡在较高位置。

排查顺序：

1. 先看训练损失曲线。如果训练损失仍在明显下降，说明可能还没训练够；如果剧烈震荡或发散，优先怀疑学习率过大或数值不稳定。
2. 看梯度范数。如果梯度爆炸、出现 `NaN/inf`，先处理学习率、初始化、归一化和梯度裁剪；如果梯度极小但损失很高，可能有梯度消失、激活饱和或初始化问题。
3. 看参数更新量。如果更新量很大且不稳定，降低学习率；如果更新量几乎为零，检查学习率是否过小、梯度是否消失、参数是否被冻结。
4. 在确认优化过程能稳定下降后，再判断表达能力。如果训练损失和验证损失都稳定停在较高水平，考虑增加特征、增大模型容量、减少过强正则化或改进模型结构。
5. 如果训练损失很低但验证损失高，则不是欠拟合，而更像过拟合。

## E. NumPy 代码训练题

### E1. 标量函数梯度检查

补全函数，使用中心有限差分近似 `f(x)=x^3-2x+1` 在 `x` 处的导数，并与解析结果 `3x²-2` 比较。

```python
def numerical_derivative(x, epsilon=1e-5):
    # 在这里完成代码
    pass
```

要求：检查 `epsilon` 为正数；分别测试 `x=-2, 0, 3`。

答案：

```python
def f(x):
    return x**3 - 2*x + 1


def analytical_derivative(x):
    return 3*x**2 - 2


def numerical_derivative(x, epsilon=1e-5):
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    return (f(x + epsilon) - f(x - epsilon)) / (2 * epsilon)


for x in [-2, 0, 3]:
    num = numerical_derivative(x)
    ana = analytical_derivative(x)
    print(x, num, ana, abs(num - ana))
```

预期解析结果：

```text
x=-2: 3*(-2)^2-2 = 10
x=0:  3*0^2-2 = -2
x=3:  3*3^2-2 = 25
```

数值差分结果应与解析结果非常接近，误差通常在 `1e-9` 到 `1e-10` 量级附近。

### E2. 二次函数梯度下降

实现最小化 `J(w)=0.5*(w-4)**2` 的函数：

```python
def minimize_quadratic(initial, learning_rate, steps):
    # 返回每一步的 w 和 loss
    pass
```

要求：验证不同学习率下的收敛、震荡和发散现象。

答案：

```python
def loss(w):
    return 0.5 * (w - 4)**2


def grad(w):
    return w - 4


def minimize_quadratic(initial, learning_rate, steps):
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")
    if steps < 0:
        raise ValueError("steps must be non-negative")

    w = float(initial)
    history = []
    for step in range(steps + 1):
        history.append((step, w, loss(w)))
        if step < steps:
            w = w - learning_rate * grad(w)
    return history


for lr in [0.1, 1.0, 1.9, 2.1]:
    hist = minimize_quadratic(initial=0, learning_rate=lr, steps=10)
    print("lr =", lr, "last =", hist[-1])
```

现象解释：

- `0 < learning_rate < 1`：通常单调接近 `w=4`。
- `1 < learning_rate < 2`：会在最优点两侧震荡，但振幅逐渐变小。
- `learning_rate = 2`：会等幅震荡，通常不收敛。
- `learning_rate > 2`：会发散。

### E3. 线性回归训练

补全以下函数，返回参数、每步损失，并拒绝形状不匹配的输入：

```python
import numpy as np

def fit_linear_gd(X, y, learning_rate=0.05, steps=1000):
    # 使用批量梯度下降
    pass
```

要求：用带噪声直线数据测试；画出损失曲线；比较三个学习率。

答案：

```python
import numpy as np
import matplotlib.pyplot as plt


def fit_linear_gd(X, y, learning_rate=0.05, steps=1000):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    if X.ndim != 2:
        raise ValueError("X must be a 2D array")
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    if y.ndim != 2 or y.shape[1] != 1:
        raise ValueError("y must have shape (n,) or (n, 1)")
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of rows")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")
    if steps < 0:
        raise ValueError("steps must be non-negative")

    n, d = X.shape
    w = np.zeros((d, 1))
    losses = []

    for _ in range(steps):
        residual = X @ w - y
        loss_value = float((residual.T @ residual) / (2 * n))
        losses.append(loss_value)
        gradient = (X.T @ residual) / n
        w -= learning_rate * gradient

    return w, np.array(losses)


rng = np.random.default_rng(0)
n = 80
xs = rng.uniform(-3, 3, size=n)
noise = rng.normal(0, 0.5, size=n)
ys = 2.5 * xs - 1.0 + noise

X = np.column_stack([xs, np.ones_like(xs)])
y = ys.reshape(-1, 1)

for lr in [0.01, 0.05, 0.2]:
    w, losses = fit_linear_gd(X, y, learning_rate=lr, steps=300)
    print("lr =", lr, "w =", w.ravel(), "final loss =", losses[-1])
    plt.plot(losses, label=f"lr={lr}")

plt.xlabel("step")
plt.ylabel("loss")
plt.legend()
plt.show()
```

若数据由 `y≈2.5x-1.0` 生成，训练后参数应接近 `[2.5, -1.0]`。学习率太小会下降慢；合适学习率会平滑下降；过大学习率可能震荡或发散。

### E4. L2 正则化实验

在 E3 的目标函数中加入 `lambda_ / 2 * sum(weights**2)`，推导并实现新的梯度。比较无正则化和两种 `lambda_` 下的参数范数与验证误差。

答案：

若不惩罚偏置项，设最后一维参数为偏置，目标函数可写为：

```text
J(w) = 1/(2n)||Xw-y||^2 + lambda_/2 * sum_{j=1}^{d-1} w_j^2
```

梯度为：

```text
∇J(w) = (1/n)X^T(Xw-y) + lambda_ * [w_1, ..., w_{d-1}, 0]^T
```

实现：

```python
import numpy as np


def fit_linear_gd_l2(X, y, learning_rate=0.05, steps=1000, lambda_=0.0):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    if X.ndim != 2:
        raise ValueError("X must be a 2D array")
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    if y.ndim != 2 or y.shape[1] != 1:
        raise ValueError("y must have shape (n,) or (n, 1)")
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of rows")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")
    if steps < 0:
        raise ValueError("steps must be non-negative")
    if lambda_ < 0:
        raise ValueError("lambda_ must be non-negative")

    n, d = X.shape
    w = np.zeros((d, 1))
    losses = []

    for _ in range(steps):
        residual = X @ w - y
        weights_without_bias = w.copy()
        weights_without_bias[-1, 0] = 0.0

        data_loss = float((residual.T @ residual) / (2 * n))
        reg_loss = float(lambda_ / 2 * np.sum(weights_without_bias**2))
        losses.append(data_loss + reg_loss)

        gradient = (X.T @ residual) / n + lambda_ * weights_without_bias
        w -= learning_rate * gradient

    return w, np.array(losses)


def mse(X, y, w):
    residual = X @ w - y
    return float(np.mean(residual**2))


rng = np.random.default_rng(1)
n = 120
xs = rng.uniform(-3, 3, size=n)
ys = 2.5 * xs - 1.0 + rng.normal(0, 0.8, size=n)
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
    print(lambda_, w.ravel(), weight_norm, val_mse)
```

通常 `lambda_` 增大时，权重范数会变小。适度正则化可能降低验证误差；过强正则化会让模型欠拟合，验证误差反而升高。

### E5. Adam 与学习率曲线

从零实现一个只依赖 NumPy 的 Adam 更新器，用它优化 `J(w)=0.5*(w-4)**2`。比较 SGD 和 Adam 在三个学习率下的损失曲线，并报告达到阈值所需的步数。

```python
class Adam:
    def __init__(self, shape, learning_rate=0.01, beta1=0.9,
                 beta2=0.999, epsilon=1e-8):
        # 初始化状态
        pass

    def step(self, weights, gradient):
        # 返回更新后的 weights
        pass
```

答案：

```python
import numpy as np
import matplotlib.pyplot as plt


class Adam:
    def __init__(self, shape, learning_rate=0.01, beta1=0.9,
                 beta2=0.999, epsilon=1e-8):
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if not 0 <= beta1 < 1:
            raise ValueError("beta1 must be in [0, 1)")
        if not 0 <= beta2 < 1:
            raise ValueError("beta2 must be in [0, 1)")
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")

        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = np.zeros(shape, dtype=float)
        self.v = np.zeros(shape, dtype=float)
        self.t = 0

    def step(self, weights, gradient):
        gradient = np.asarray(gradient, dtype=float)
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradient
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradient**2)
        m_hat = self.m / (1 - self.beta1**self.t)
        v_hat = self.v / (1 - self.beta2**self.t)
        return weights - self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)


def quadratic_loss(w):
    return 0.5 * (w - 4)**2


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
        f"lr={lr}: "
        f"SGD reached={sgd_reached}, final={sgd_losses[-1]:.3e}; "
        f"Adam reached={adam_reached}, final={adam_losses[-1]:.3e}"
    )
    plt.plot(sgd_losses, "--", label=f"SGD lr={lr}")
    plt.plot(adam_losses, label=f"Adam lr={lr}")

plt.yscale("log")
plt.xlabel("step")
plt.ylabel("loss")
plt.legend()
plt.show()
```

报告步数时，如果输出为 `None`，表示在给定步数内没有达到阈值。SGD 在这个简单二次问题上也能很好工作；Adam 的优势通常在高维、梯度尺度差异大或噪声较强的问题上更明显。

### E6. 两层网络反传检查

使用 NumPy 实现一个带 ReLU 的两层网络和平方损失，分别计算解析梯度与有限差分梯度，报告最大绝对误差。测试至少包含一个 ReLU 激活值接近 0 的输入。

答案：

```python
import numpy as np


def forward(params, x, y):
    W1, b1, W2, b2 = params["W1"], params["b1"], params["W2"], params["b2"]
    z = W1 @ x + b1
    h = np.maximum(z, 0.0)
    o = W2 @ h + b2
    diff = o - y
    loss = 0.5 * float(diff.T @ diff)
    cache = {"x": x, "y": y, "z": z, "h": h, "o": o, "diff": diff}
    return loss, cache


def backward(params, cache):
    x, z, h, diff = cache["x"], cache["z"], cache["h"], cache["diff"]
    W2 = params["W2"]

    do = diff
    dW2 = do @ h.T
    db2 = do
    dh = W2.T @ do
    dz = dh * (z > 0)
    dW1 = dz @ x.T
    db1 = dz

    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}


def numerical_grads(params, x, y, epsilon=1e-5):
    grads = {}
    for name, value in params.items():
        grad = np.zeros_like(value)
        it = np.nditer(value, flags=["multi_index"], op_flags=["readwrite"])
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
    "b2": rng.normal(0, 0.2, size=(c, 1)),
}

x = rng.normal(size=(d, 1))
y = rng.normal(size=(c, 1))

# 人为构造一个接近 ReLU 拐点的隐藏单元。
params["b1"][0, 0] = -float(params["W1"][0:1] @ x) + 1e-4

loss_value, cache = forward(params, x, y)
analytic = backward(params, cache)
numeric = numerical_grads(params, x, y)

max_error = 0.0
for name in params:
    error = np.max(np.abs(analytic[name] - numeric[name]))
    max_error = max(max_error, float(error))
    print(name, error)

print("loss =", loss_value)
print("max absolute error =", max_error)
```

如果没有参数正好落在 ReLU 不可导点，解析梯度和数值梯度的最大绝对误差通常应在 `1e-6` 到 `1e-8` 附近。若激活值非常接近 `0`，误差可能变大，因为 ReLU 在 `0` 处不可导，有限差分会跨过拐点。

## F. 本周验收

完成本文件和代码实验后，请用自己的话回答：

1. 我能否从目标函数推导梯度，而不是只调用自动求导？
2. 我能否根据损失曲线判断学习率问题？
3. 我能否解释梯度、Hessian、正则化和特征缩放的联系？
4. 我还不理解的地方是：

答案：

1. 可以。对简单标量函数、多元二次函数、线性回归平方损失和两层网络，我能从目标函数出发，用链式法则推导出参数梯度；自动求导可以作为工具，但我需要理解它背后的计算图和局部导数相乘。
2. 可以初步判断。损失平滑下降通常说明学习率较合适；下降很慢说明学习率可能过小；明显震荡说明学习率偏大；损失变成越来越大、`inf` 或 `NaN` 时，通常说明学习率过大或存在数值稳定性问题。
3. 可以。梯度决定一阶下降方向，Hessian 描述局部曲率和极值类型；正则化通过改变目标函数的形状约束参数规模；特征缩放会改善损失曲面的条件数，让梯度下降更稳定、更快。
4. 还需要继续加强的是：在更复杂网络中判断学习率、初始化、归一化和正则化之间的相互影响；以及对 Adam 等自适应优化器在真实任务中为何有时泛化不如 SGD 的理解。
