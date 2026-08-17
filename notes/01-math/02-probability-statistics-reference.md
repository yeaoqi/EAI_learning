# 02 概率、统计与实验规范自测参考答案

> 说明：这份文件按原题号给出参考答案。概念题重在理解，编程题给出一种可运行写法；实际作业时可以用自己的语言重新组织。

## A. 概率基础

### A1. 随机事件与概率

样本空间是一次随机试验中所有可能结果组成的集合，通常记为 `Omega`。例如掷一枚硬币，样本空间可以是 `{正面, 反面}`。

随机事件是样本空间的一个子集，表示我们关心的一类结果。例如“掷骰子得到偶数”就是事件 `{2, 4, 6}`。

概率为 `0` 或 `1` 在有限样本空间中通常对应“不可能”和“必然”。但在连续型随机变量中，某个精确点的概率可以为 `0`，却不是逻辑上不可能。例如从 `[0, 1]` 均匀随机取一个数，取到 `0.5` 的概率为 `0`，但 `0.5` 仍在可能取值范围内。类似地，概率为 `1` 表示“几乎必然”，不一定等于逻辑必然。

### A2. 联合概率、边缘概率与条件概率

联合概率 `P(A, B)` 或 `P(A ∩ B)` 表示事件 `A` 和事件 `B` 同时发生的概率。

边缘概率 `P(A)` 表示只关心事件 `A` 是否发生，而不管其他变量或事件取什么值。

条件概率 `P(A | B)` 表示在已知 `B` 已经发生的条件下，`A` 发生的概率：

```text
P(A | B) = P(A ∩ B) / P(B),  P(B) > 0
```

三者关系可以写成：

```text
P(A ∩ B) = P(A | B)P(B) = P(B | A)P(A)
P(A) = sum_b P(A, B=b)
```

### A3. 独立与互斥

独立表示两个事件是否发生互不影响：

```text
P(A ∩ B) = P(A)P(B)
```

互斥表示两个事件不能同时发生：

```text
P(A ∩ B) = 0
```

如果 `A` 和 `B` 都是非零概率事件，它们不能同时既独立又互斥。因为互斥给出 `P(A ∩ B)=0`，独立要求 `P(A ∩ B)=P(A)P(B)`，若 `P(A)>0` 且 `P(B)>0`，则 `P(A)P(B)>0`，矛盾。

### A4. 全概率公式

如果事件 `B1, B2, ..., Bn` 构成样本空间的一个划分，也就是两两互斥且并集为全集，并且 `P(Bi)>0`，则：

```text
P(A) = sum_i P(A | Bi)P(Bi)
```

机器人感知例子：机器人要判断“前方有障碍物”这个事件 `A`。环境状态可以分为 `B1=室内强光`、`B2=正常光照`、`B3=昏暗光照`。每种环境出现概率不同，传感器在不同环境下检测到障碍物的概率也不同，那么总体检测概率可以用全概率公式加权求和。

### A5. 贝叶斯公式

贝叶斯公式：

```text
P(A | B) = P(B | A)P(A) / P(B)
```

其中：

- `P(A)` 是先验概率：看到当前证据之前，对事件 `A` 的相信程度。
- `P(B | A)` 是似然：如果 `A` 为真，观察到证据 `B` 的概率。
- `P(A | B)` 是后验概率：看到证据 `B` 之后，对事件 `A` 的更新相信程度。
- `P(B)` 是证据或归一化常数，保证所有后验概率加起来为 `1`。它也可以由全概率公式计算。

### A6. 医疗检测问题

直觉上，很多人会以为检测阳性后患病概率接近 `95%`，但因为疾病患病率只有 `1%`，假阳性会占很大比例。

设 `D` 表示患病，`+` 表示检测阳性：

```text
P(D) = 0.01
P(+ | D) = 0.95
P(+ | not D) = 0.05
P(not D) = 0.99
```

由贝叶斯公式：

```text
P(D | +)
= P(+ | D)P(D) / [P(+ | D)P(D) + P(+ | not D)P(not D)]
= 0.95 * 0.01 / (0.95 * 0.01 + 0.05 * 0.99)
= 0.0095 / 0.059
≈ 0.161
```

所以检测阳性后真正患病的概率约为 `16.1%`。

## B. 随机变量与常见分布

### B1. 随机变量

随机变量是把随机试验结果映射成数值的函数。例如掷骰子的点数 `X` 就是随机变量。普通程序变量通常表示一次确定计算中的某个值；随机变量强调它的值在试验前不确定，并服从某种概率分布。

离散随机变量的取值是有限或可数的，例如一次抓取是否成功、100 次抓取成功次数。连续随机变量的取值落在连续区间中，例如测量误差、温度、位置偏差。

### B2. 概率质量函数与概率密度函数

PMF 用于离散随机变量，给出每个具体取值的概率，例如 `P(X=k)`。

PDF 用于连续随机变量，本身不是“点概率”，而是概率密度。连续变量落在区间 `[a,b]` 内的概率由积分得到：

```text
P(a <= X <= b) = integral_a^b f(x) dx
```

连续随机变量在某个精确点上的概率通常为 `0`，因为点的区间宽度为 `0`。但概率密度可以大于 `0`，甚至可以大于 `1`，只要整个取值范围上的积分为 `1`。

CDF 是累积分布函数：

```text
F(x) = P(X <= x)
```

它表示随机变量小于等于某个值的累计概率。

### B3. 伯努利分布与二项分布

伯努利分布描述一次只有成功/失败两种结果的试验，参数为成功概率 `p`。

二项分布描述 `n` 次独立伯努利试验中成功的次数，参数为 `n` 和 `p`。可以理解为多个独立伯努利试验的总和。

使用场景：

- 伯努利分布：一次机器人抓取是否成功。
- 二项分布：100 次机器人抓取中成功了多少次。

### B4. 高斯分布

高斯分布也叫正态分布，主要由均值 `mu` 和方差 `sigma^2` 决定：

- `mu` 控制分布中心位置。
- `sigma^2` 或标准差 `sigma` 控制分布分散程度。

实验噪声常被近似为高斯分布，是因为很多误差来源可以看作许多小的、相互独立的扰动叠加；根据中心极限定理，它们的总和往往接近正态分布。

### B5. Beta 分布

Beta 分布的取值范围是 `[0, 1]`，因此适合表示未知概率参数，例如硬币正面概率、抓取成功率、分类器准确率等。

`Beta(alpha, beta)` 中：

- `alpha` 可以粗略理解为“正面/成功”的先验计数。
- `beta` 可以粗略理解为“反面/失败”的先验计数。

`alpha` 和 `beta` 越大，先验越强；二者接近时分布更偏向中间，差异大时分布更偏向某一端。

### B6. 分布选择

一次抓取是否成功：伯努利分布，因为只有成功和失败两种结果。

100 次抓取中的成功次数：二项分布，因为它是固定次数独立伯努利试验的成功总数。

相机测量误差：高斯分布，很多测量误差可近似看作多个小扰动的叠加。

每分钟收到的故障消息数量：泊松分布，因为它常用于描述固定时间窗口内随机事件发生的次数。

## C. 期望、方差与协方差

### C1. 期望

期望表示随机变量的长期平均水平或概率加权平均值。离散情形：

```text
E[X] = sum_x x P(X=x)
```

连续情形：

```text
E[X] = integral x f(x) dx
```

期望不一定是随机变量能实际取到的值。例如公平骰子的期望是 `3.5`，但骰子不可能掷出 `3.5`。

### C2. 方差与标准差

方差衡量随机变量围绕均值的离散程度：

```text
Var(X) = E[(X - E[X])^2]
```

标准差是方差的平方根：

```text
std(X) = sqrt(Var(X))
```

标准差和原变量单位一致，所以实验报告中更容易解释；方差在数学推导中更常用，因为平方形式便于求导、分解和代数运算。

### C3. 线性变换

若 `Y = aX + b`，且 `E[X]=mu`、`Var(X)=sigma^2`，则：

```text
E[Y] = a mu + b
Var(Y) = a^2 sigma^2
```

平移 `b` 改变均值，但不改变方差；缩放 `a` 会让方差乘以 `a^2`。

### C4. 协方差与相关系数

协方差：

```text
Cov(X,Y) = E[(X-E[X])(Y-E[Y])]
```

协方差为正，表示两个变量倾向于同向变化；为负，表示倾向于反向变化；接近 `0`，表示线性关系弱。

协方差受量纲影响。例如长度从米改成厘米，协方差数值会跟着改变。

相关系数是标准化后的协方差：

```text
rho = Cov(X,Y) / (std(X)std(Y))
```

它的取值范围是 `[-1, 1]`，不受单位影响，更方便比较线性相关强弱。

相关系数为 `0` 不一定表示两个变量独立，只能说明无线性相关。独立通常可以推出相关系数为 `0`，但反过来不一定成立。

### C5. 样本统计量

总体均值和总体方差描述整个总体的真实参数，通常未知。样本均值和样本方差是根据抽样数据计算出来的统计量，用于估计总体参数。

无偏样本方差常用：

```text
s^2 = 1/(n-1) * sum_i (x_i - x_bar)^2
```

使用 `n-1` 是因为样本均值 `x_bar` 已经由数据估计出来，消耗了一个自由度。用 `n` 会系统性低估总体方差，而用 `n-1` 可以得到总体方差的无偏估计。

## D. MLE 与 MAP

### D1. 似然

概率通常是在参数已知时，问某个数据或事件发生的可能性。例如已知硬币正面概率 `p=0.6`，问抛出某组结果的概率。

似然是在观测数据已经固定时，把参数看作变量，问“哪个参数最能解释这组数据”。例如已经观察到 `10` 次中 `7` 次正面，把 `p` 当作变量，写出 `L(p)`。

### D2. 最大似然估计

MLE 想找的是使观测数据出现概率最大的参数：

```text
theta_MLE = argmax_theta P(data | theta)
```

实际推导中常最大化对数似然，因为多个概率相乘容易数值下溢，而取对数可以把乘法变成加法：

```text
log(a*b) = log(a) + log(b)
```

对数函数单调递增，所以最大化似然和最大化对数似然得到的参数相同。

### D3. 硬币的 MLE

独立抛硬币 `n` 次，其中 `k` 次正面，正面概率为 `p`。

似然函数：

```text
L(p) = p^k (1-p)^(n-k)
```

如果关心具体序列数量，也可以乘上组合系数 `C(n,k)`；但该系数与 `p` 无关，不影响 MLE。

对数似然：

```text
ell(p) = k log p + (n-k) log(1-p)
```

求导：

```text
d ell / dp = k/p - (n-k)/(1-p)
```

令导数为 `0`：

```text
k/p = (n-k)/(1-p)
k(1-p) = p(n-k)
k = np
p_MLE = k/n
```

所以硬币正面概率的最大似然估计是样本正面比例。

### D4. 最大后验估计

MLE 最大化的是：

```text
P(data | theta)
```

MAP 最大化的是：

```text
P(theta | data) ∝ P(data | theta)P(theta)
```

MAP 会把先验 `P(theta)` 纳入估计。数据很少时，先验影响较大，可以避免估计过于极端；数据很多时，似然项通常占主导，MAP 和 MLE 往往越来越接近。

### D5. Beta-Bernoulli MAP

先验：

```text
p ~ Beta(alpha, beta)
```

观测到 `k` 次正面和 `n-k` 次反面后，后验仍是 Beta 分布：

```text
p | data ~ Beta(alpha + k, beta + n - k)
```

也就是说：

```text
alpha_post = alpha + k
beta_post = beta + n - k
```

当 `alpha_post > 1` 且 `beta_post > 1` 时，MAP 为：

```text
p_MAP = (alpha_post - 1) / (alpha_post + beta_post - 2)
      = (alpha + k - 1) / (alpha + beta + n - 2)
```

使用均匀先验 `Beta(1,1)` 时：

```text
p_MAP = k/n
```

在非边界情况下，MAP 与 MLE 相同。若数据全是正面或全是反面，要注意 MAP 可能落在边界。

### D6. MLE、MAP 与过拟合

数据量很少时，MLE 只看当前观测，容易得到极端估计。例如只抛硬币 `2` 次且都为正面，MLE 会给出 `p=1`，这通常过于自信。

先验在 MAP 中相当于正则化：它把估计拉向先验认为更合理的区域，减少小样本偶然性造成的极端结果。随着数据增加，真实观测会逐渐压过先验影响。

## E. 抽样、置信区间与实验结果

### E1. 总体与样本

总体是研究对象的完整集合，例如所有可能抓取任务的表现。样本是从总体中抽取的一部分观测。抽样是获得样本的过程。

现实中总体往往太大、成本太高或无法完全观测，所以通常只能通过样本估计总体。样本是否随机、是否有偏，会影响估计的可靠性。

### E2. 大数定律

大数定律说明：在独立同分布且期望存在的条件下，样本均值会随着样本量增加而趋近总体期望。

它不表示每一次单独观测都会越来越接近期望。单次观测仍然可能波动很大，只是大量观测的平均值更稳定。

### E3. 中心极限定理

中心极限定理说明：在一定条件下，很多独立同分布样本的均值经过标准化后，会近似服从正态分布，即使原始数据本身不服从正态分布。

它对实验均值和置信区间很有用，因为我们常关心“样本均值离真实均值有多远”。中心极限定理让我们可以用正态分布或 t 分布近似描述样本均值的不确定性。

### E4. 标准差与标准误

标准差描述单个观测值的波动程度。

标准误描述样本均值的波动程度，常写为：

```text
SE = s / sqrt(n)
```

当样本量 `n` 增加时，标准差通常不会因为样本量变大而明显下降，因为单次观测本身的波动还在；标准误通常会按 `1/sqrt(n)` 下降，因为均值估计更稳定。

### E5. 置信区间

“均值的 95% 置信区间”更准确的解释是：如果重复抽样并用同样的方法构造区间，长期来看大约 `95%` 的区间会包含真实均值。

题目中的第 `2` 种说法更准确。第 `1` 种说法容易把固定后的区间理解成“真均值以 95% 概率在其中”。在频率派解释中，真实均值是固定的，当前区间也是固定的，它要么包含真均值，要么不包含。

### E6. 置信区间宽度

样本量增加：置信区间通常变窄，因为标准误 `s/sqrt(n)` 变小。

实验波动增大：置信区间通常变宽，因为样本标准差 `s` 变大。

置信水平从 `95%` 提高到 `99%`：置信区间变宽，因为为了更高覆盖率，需要更大的临界值。

### E7. 多随机种子实验

只报告最好的一次结果会误导读者，因为最好结果可能只是随机波动带来的偶然值，不能代表方法的稳定表现。

至少应该报告：

- 多个随机种子的每次结果。
- 均值。
- 标准差或标准误。
- 最小值和最大值。
- 置信区间。
- 必要时报告失败案例和异常运行。

### E8. 统计显著性与实际价值

统计显著性表示观察到的差异不太像纯随机波动造成，但不一定说明差异有实际价值。

效应大小表示差异有多大，例如成功率提升 `0.2%` 还是 `10%`。实际价值还要考虑成本、部署风险、计算开销、稳定性和业务目标。

因此，“差异具有统计显著性”只能说明证据支持存在差异，不能自动说明改进值得部署。

## F. 实验规范与可复现性

### F1. 可复现的实验

至少应记录：

- 代码：仓库地址、Git commit ID、运行脚本、关键函数版本。
- 环境：操作系统、Python 版本、依赖库版本、硬件型号、GPU/CUDA 版本。
- 数据：数据来源、版本、划分方式、预处理步骤、是否过滤样本。
- 配置：模型参数、训练参数、实验参数、命令行参数。
- 随机性：随机种子、随机数生成器、是否使用非确定性算子。
- 输出：指标、日志、模型文件、图表、失败样例。

### F2. 随机种子

固定随机种子可以让伪随机过程在相同环境中生成相同序列，便于复现实验和定位问题。

但固定种子不能保证所有硬件和运行环境下完全相同。并行计算、GPU 非确定性算子、库版本差异、浮点舍入差异都可能导致结果不同。

### F3. 对照实验

基线是用于比较的已有方法或简单方法。对照组是实验中不接受新处理或使用标准处理的组。

比较两个方法时，应尽量保持一致：

- 数据集与划分。
- 训练轮数和预算。
- 硬件与运行环境。
- 随机种子或种子集合。
- 评估指标。
- 超参数搜索预算。
- 预处理和后处理流程。

### F4. 数据泄漏

训练集用于训练模型，验证集用于调参和模型选择，测试集用于最终评估泛化能力。

可能造成数据泄漏的操作包括：

- 在全量数据上做归一化、特征选择后再划分数据。
- 用测试集反复调参。
- 训练样本和测试样本重复或高度相似。
- 标签信息被编码进特征。
- 时间序列任务中使用了未来信息。

测试集不应反复用于调参，因为每次根据测试集改模型，都会让模型间接适应测试集，最终测试结果会偏乐观。

### F5. 指标选择

100 次测试成功 90 次，除了成功率，还应记录：

- 失败原因分类。
- 每次抓取耗时。
- 目标物体类别、姿态、材质和场景难度。
- 抓取稳定性和掉落率。
- 碰撞、损坏、安全问题。
- 成功判定标准。
- 多次运行的均值、方差、置信区间。
- 异常样例和日志。

### F6. 失败样例

失败样例能暴露方法的边界条件和系统性弱点，只保存成功案例会让实验结论过于乐观。

失败可以按原因分类，例如：

- 感知失败：识别错误、定位偏差、遮挡。
- 规划失败：路径不可达、碰撞。
- 控制失败：执行偏差、夹爪力度不合适。
- 环境因素：光照、反光、物体滑动。
- 数据问题：标注错误、分布外样本。

### F7. 实验假设

可以改写为：

```text
在相同数据集、相同训练预算、相同随机种子集合和相同评估指标下，
新方法在 1000 次抓取测试中的平均成功率相比基线方法至少提升 3 个百分点，
且 95% 置信区间的下界仍高于基线平均成功率。
```

这个假设具体、可测量，也可能被实验结果证伪。

## G. NumPy 编程理解题

### G1. 描述性统计

代码输出依次表示：

```python
np.mean(scores)          # 样本均值
np.var(scores, ddof=1)   # 无偏样本方差
np.std(scores, ddof=1)   # 样本标准差
np.median(scores)        # 中位数
```

对给定数据：

```text
mean   = 0.786
var    = 0.00233
std    ≈ 0.04827
median = 0.79
```

`ddof=1` 表示方差分母使用 `n-1`，用于计算无偏样本方差；默认 `ddof=0` 时分母是 `n`。

均值容易受极端值影响，中位数对极端值更稳健。方差的单位是原变量单位的平方，标准差的单位与原变量一致。

### G2. 随机数生成器

`loc` 是正态分布均值，`scale` 是标准差，`size` 是生成样本数量。

`rng1` 和 `rng2` 使用相同种子 `42` 创建，并且调用顺序相同，所以 `x1` 和 `x2` 相同。

推荐为实验创建独立随机数生成器，是为了避免不同模块共享全局随机状态，导致调用顺序变化后结果难以复现。

### G3. 模拟伯努利试验

```python
import numpy as np

def simulate_success_rate(p, n, seed):
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1]")
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

    rng = np.random.default_rng(seed)
    trials = rng.random(n) < p
    return trials.mean()

for n in [10, 100, 10000]:
    print(n, simulate_success_rate(p=0.7, n=n, seed=42))
```

一般来说，`n=10` 时结果波动较大，`n=100` 更接近真实概率，`n=10000` 通常会非常接近 `p=0.7`。但单次模拟仍有随机波动。

也可以用：

```python
trials = rng.binomial(1, p, size=n)
```

### G4. 手动计算统计量

```python
import numpy as np

def sample_statistics(values):
    """返回样本均值、无偏样本方差和样本标准差。"""
    x = np.asarray(values, dtype=float)
    n = x.size
    if n < 2:
        raise ValueError("at least two values are required")

    mean = x.sum() / n
    centered = x - mean
    var = np.sum(centered ** 2) / (n - 1)
    std = np.sqrt(var)
    return mean, var, std

values = np.array([0.72, 0.81, 0.76, 0.85, 0.79])
mean, var, std = sample_statistics(values)

print(mean, np.mean(values))
print(var, np.var(values, ddof=1))
print(std, np.std(values, ddof=1))
```

如果样本数量小于 `2`，无偏样本方差没有定义，因此应该抛出错误或返回明确的缺失值。

## H. 编程与实验题

### H1. MLE 与 MAP 硬币实验

参考实现：

```python
import numpy as np

def coin_estimates(true_p=0.7, ns=(5, 20, 100, 1000), priors=((1, 1), (2, 2), (8, 2)), seed=42):
    rng = np.random.default_rng(seed)
    rows = []

    for n in ns:
        data = rng.random(n) < true_p
        k = int(data.sum())
        mle = k / n

        row = {"n": n, "k": k, "true_p": true_p, "mle": mle}
        for alpha, beta in priors:
            alpha_post = alpha + k
            beta_post = beta + n - k
            if alpha_post > 1 and beta_post > 1:
                map_est = (alpha_post - 1) / (alpha_post + beta_post - 2)
            else:
                map_est = 0.0 if alpha_post <= 1 else 1.0
            row[f"map_beta_{alpha}_{beta}"] = map_est
        rows.append(row)

    return rows

for row in coin_estimates():
    print(row)
```

结论要点：

- 小样本时 MAP 更容易受先验影响。
- 如果先验严重错误，小样本 MAP 可能被拉向错误方向。
- 数据增多后，MLE 和 MAP 通常逐渐接近真实值，也彼此接近。

### H2. 多随机种子实验

参考实现：

```python
import numpy as np

def run_once(seed, true_p=0.7, n=100):
    rng = np.random.default_rng(seed)
    return (rng.random(n) < true_p).mean()

seeds = range(10)
results = np.array([run_once(seed) for seed in seeds])

print("results:", results)
print("mean:", results.mean())
print("sample std:", results.std(ddof=1))
print("min:", results.min())
print("max:", results.max())
print("best - mean:", results.max() - results.mean())
```

结论：只报告最好的一次会高估方法表现。平均值和标准差能更好反映方法的典型表现和稳定性。

### H3. 均值的置信区间

小样本且总体方差未知时，优先使用 t 分布：

```python
import numpy as np
from scipy import stats

def mean_confidence_interval(values, confidence=0.95):
    """返回样本均值、置信区间下界和上界。"""
    x = np.asarray(values, dtype=float)
    n = x.size
    if n < 2:
        raise ValueError("at least two values are required")

    mean = x.mean()
    s = x.std(ddof=1)
    se = s / np.sqrt(n)
    alpha = 1 - confidence
    t_crit = stats.t.ppf(1 - alpha / 2, df=n - 1)
    margin = t_crit * se
    return mean, mean - margin, mean + margin
```

公式含义：

- `mean` 是样本均值。
- `s` 是样本标准差。
- `se = s/sqrt(n)` 是样本均值的标准误。
- `t_crit` 是置信水平对应的 t 分布临界值。
- `margin` 是误差半径。

若使用第三方库，应记录例如 `scipy` 及其版本。样本量越大，区间越窄；方差越大，区间越宽。

### H4. 置信区间覆盖率模拟

```python
import numpy as np
from scipy import stats

def ci_t(values, confidence=0.95):
    x = np.asarray(values, dtype=float)
    n = x.size
    mean = x.mean()
    se = x.std(ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf(1 - (1 - confidence) / 2, df=n - 1)
    return mean - t_crit * se, mean + t_crit * se

def coverage_simulation(n, repeats=1000, true_mu=0.0, true_sigma=1.0, seed=42):
    rng = np.random.default_rng(seed)
    covered = 0
    for _ in range(repeats):
        sample = rng.normal(true_mu, true_sigma, size=n)
        low, high = ci_t(sample)
        covered += low <= true_mu <= high
    return covered / repeats

for n in [5, 20, 100]:
    print(n, coverage_simulation(n))
```

实际覆盖率不会刚好等于 `95%`，因为模拟次数有限，会有随机误差；另外如果分布假设或近似条件不满足，覆盖率也可能偏离 `95%`。

### H5. 可复现实验检查

参考程序框架：

```python
import argparse
import json
import platform
import subprocess
from pathlib import Path

import numpy as np

def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=float, default=0.7)
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="experiment-result.json")
    args = parser.parse_args()

    if not 0 <= args.p <= 1:
        raise ValueError("p must be in [0, 1]")
    if args.n <= 0:
        raise ValueError("n must be positive")

    rng = np.random.default_rng(args.seed)
    success_rate = float((rng.random(args.n) < args.p).mean())

    result = {
        "config": vars(args),
        "result": {"success_rate": success_rate},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "git_commit": git_commit(),
        },
    }

    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```

用完全相同配置运行两次，如果环境和依赖一致，结果文件中的核心结果应一致。

## I. 结果分析题

### I1. 比较两种方法

方法 A：

```text
mean = 0.80
sample std ≈ 0.0158
```

方法 B：

```text
mean = 0.79
sample std ≈ 0.1194
```

平均表现：方法 A 略好，因为均值更高。

稳定性：方法 A 明显更稳定，因为样本标准差更小。

如果只比较最好结果，会认为方法 B 更好，因为方法 B 的最高值 `0.93` 高于方法 A 的最高值 `0.82`。这会忽略 B 的巨大波动。

当前数据只有每个方法 5 次运行，样本量较小。还需要更多随机种子、相同实验预算、置信区间、显著性检验、运行成本、失败案例等信息，才能判断是否值得部署。

### I2. 发现实验问题

主要问题：

- 新方法在测试集上反复调参，造成测试集泄漏。
- 新方法报告最好一次结果，而不是多次运行统计。
- 基线只用默认参数运行一次，比较不公平。
- 没有报告方差、置信区间和随机种子。
- “提升 5%”表述不清，可能是 5 个百分点，也可能是相对提升。

改进方案：

- 划分训练集、验证集和测试集。
- 只在验证集上调参，测试集只用于最终一次评估。
- 给基线和新方法相同调参预算。
- 使用多个随机种子重复实验。
- 报告均值、标准差、置信区间、最好/最差结果和失败案例。

### I3. 解读重叠的置信区间

两个方法的 95% 置信区间重叠，不一定说明它们没有显著差异。单独均值置信区间的重叠与“均值差异的置信区间”或假设检验不是一回事。

更严谨的比较应考虑：

- 是否是配对实验。
- 比较的是两个均值，还是每个样本上的差值。
- 均值差的置信区间。
- t 检验、置换检验或 bootstrap。
- 样本量和方差。
- 多重比较问题。
- 效应大小和实际部署价值。

## J. 本周验收

可以这样总结：

条件概率和贝叶斯公式用于在已有证据下更新判断，例如检测阳性后重新估计患病概率，或传感器给出读数后更新环境状态判断。

MLE 只根据数据选择最可能的参数；MAP 在数据之外还加入先验，因此小样本时更稳健，但也可能受错误先验影响。

方差和标准差描述单个观测的波动，标准误描述样本均值的不确定性，置信区间描述用当前方法估计总体均值时的不确定范围。

随机实验需要多个种子，因为单次结果可能偶然偏高或偏低。报告均值、方差和区间比只报告最好结果更可靠。

可复现实验需要记录代码版本、环境、数据、配置、随机种子和输出结果，这样别人或未来的自己才能复查结论。

仍不理解的地方可以重点回看：连续变量点概率、MAP 的先验作用、置信区间的频率派解释。

## K. 建议交付物

Week 2 建议至少保留：

- 自测题答案。
- MLE/MAP 硬币实验代码和结果。
- 多随机种子实验代码和统计结果。
- 均值置信区间或覆盖率模拟实验。
- 按 `templates/experiment-log.md` 填写的实验日志。
- Week 2 周复盘，说明已掌握内容、仍不清楚的问题和下一步补强计划。
