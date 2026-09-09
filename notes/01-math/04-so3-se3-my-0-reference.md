# 04 SO(3) 与 SE(3) 参考答案

这份文件按原题号整理参考答案，尽量把题目带上，方便你直接对照复习。  
建议先独立做一遍，再回来查漏补缺。

## A. 坐标系与旋转基础

### A1. 题目
> 几何向量和“它在某个坐标系下的坐标”有什么区别？同一个空间对象为什么在不同坐标系下会有不同数值？

答案：

几何向量是“对象本身”，坐标是“在某个基下的表示”。
同一个点或向量换了坐标系，几何意义不变，但数值会变。

更准确地说：

- 点表示空间中的位置
- 向量表示方向和长度
- 坐标是对象在某个坐标系基底下的分量

例如，若 `p` 是一个点，它在 `{A}` 和 `{B}` 中的坐标可以不同；但它指向的同一个空间位置没有变。

### A2. 题目
> 请解释主动旋转和被动变换的区别。为什么它们常常写出同样形式的旋转矩阵？阅读公式时如何判断作者采用的是哪种约定？

答案：

- 主动旋转：把几何对象本身转过去
- 被动变换：坐标系变了，对同一个对象重新记坐标

两者在矩阵形式上常写得很像，因为本质上都在描述“两个坐标表示之间的对应关系”，只是解释方向不同。

判断约定时重点看：

- `R` 是把 B 系坐标变到 A 系，还是把 A 系向量主动转到新方向
- 下标顺序是否明确，例如 `R_ab` 到底表示 `B -> A` 还是 `A -> B`
- 公式里是左乘还是右乘

### A3. 题目
> 三维矩阵 `R` 属于 `SO(3)` 需要满足哪些条件？请解释 `R^T R = I`、`det(R)=1`、`R^{-1}=R^T` 的含义。

答案：

旋转矩阵 `R` 属于 `SO(3)` 当且仅当：

```text
R^T R = I
det(R) = 1
```

含义分别是：

- `R^T R = I`：列向量两两正交且长度为 1，说明旋转不改变长度和夹角
- `det(R) = 1`：保持右手系，不发生镜像翻转
- `R^{-1} = R^T`：正交矩阵的逆等于转置，所以旋转可以用转置方便地反向变换

### A4. 题目
> 写出绕 `x`、`y`、`z` 轴旋转角 `theta` 的基本旋转矩阵。令 `point=[1,0,0]^T` 绕 `z` 轴主动旋转 `90°`，手算旋转后的坐标，并检查长度是否保持不变。

答案：

绕 `z` 轴旋转 `theta` 的矩阵：

```text
[ cos(theta)  -sin(theta)   0 ]
[ sin(theta)   cos(theta)   0 ]
[     0            0        1 ]
```

绕 `z` 轴主动旋转 `90°` 后：

```text
[1,0,0]^T -> [0,1,0]^T
```

长度：

```text
||[1,0,0]|| = 1
||[0,1,0]|| = 1
```

所以旋转只改方向，不改模长。

### A5. 题目
> 若 `R_ab` 把 `{B}` 中的坐标变到 `{A}`，`R_bc` 把 `{C}` 中的坐标变到 `{B}`，推导 `R_ac`，并解释为什么矩阵乘法顺序不能随意交换。

答案：

```text
R_ac = R_ab R_bc
```

原因是复合变换的含义是“先把 `C` 变到 `B`，再把 `B` 变到 `A`”。  
矩阵乘法不交换，所以顺序一旦变了，得到的就不是同一个几何变换。

### A6. 题目
> 已知两个姿态在世界系下的旋转矩阵 `R_world_1` 和 `R_world_2`，如何求从姿态 1 到姿态 2 的相对旋转？

答案：

一种常见写法是：

```text
R_21 = R_world_2^T R_world_1
```

本质上是“先回到世界系，再去到目标姿态系”。  
但一定要把坐标约定写清楚，因为不同教材对下标和左右乘的约定可能不同。

## B. 欧拉角、轴角与四元数

### B1. 题目
> 什么是欧拉角？内旋与外旋、`XYZ` 与 `ZYX` 分别表示什么？为什么只给出三个角度还要强调顺序？

答案：

欧拉角是一种用三个角描述姿态的参数化方式。  
关键点是“旋转顺序”本身就是定义的一部分。

- 内旋：后一个旋转轴是跟着刚体一起转的
- 外旋：旋转轴固定在空间中不动

`XYZ` 和 `ZYX` 表示不同顺序的组合，得到的姿态一般不同，所以顺序不能省略。

### B2. 题目
> 以常见的 `ZYX` 欧拉角为例，解释 pitch 接近 `±90°` 时发生了什么。gimbal lock 是物体失去了真实自由度，还是欧拉角参数化出现了奇异性？它会带来哪些数值或控制问题？

答案：

当 pitch 接近 `±90°` 时，两个旋转轴会对齐，导致两个角度变得耦合，欧拉角参数化退化。

这不是刚体真的少了自由度，而是欧拉角表达出现了奇异性。

常见影响：

- yaw 和 roll 的数值会突然跳变
- 角度恢复不稳定
- 插值会变差
- 控制器可能因为角度跳变产生异常指令

### B3. 题目
> 轴角表示由哪些量组成？写出单位旋转轴 `axis` 的反对称矩阵 `[axis]_x`，并使用 Rodrigues 公式表示旋转矩阵；说明 `theta=0` 时的结果。

答案：

轴角由：

- 单位旋转轴 `axis`
- 旋转角 `theta`

组成。

反对称矩阵：

```text
[axis]_x = [   0    -az    ay ]
          [  az     0    -ax ]
          [ -ay    ax     0  ]
```

Rodrigues 公式：

```text
R = I + sin(theta)[axis]_x + (1-cos(theta))[axis]_x^2
```

当 `theta = 0` 时：

```text
R = I
```

### B4. 题目
> 写出三维向量 `vector=[v1,v2,v3]^T` 对应的反对称矩阵 `[vector]_x`，并验证 `[vector]_x point = vector x point`。

答案：

```text
[vector]_x = [  0   -v3   v2 ]
             [  v3    0   -v1 ]
             [ -v2   v1    0  ]
```

它满足对任意 `point`：

```text
[vector]_x point = vector x point
```

这是叉乘的矩阵化表达。

### B5. 题目
> 单位四元数 `quaternion=[w,x,y,z]` 中实部、虚部与轴角是什么关系？单位四元数约束是什么？不同库为什么会采用不同分量顺序？

答案：

四元数可以写成：

```text
q = [w, x, y, z]
```

其中：

- `w` 是实部
- `[x,y,z]` 是虚部，也叫向量部

单位约束：

```text
w^2 + x^2 + y^2 + z^2 = 1
```

不同库分量顺序不同，通常只是工程约定，不是数学本体不同。  
使用时必须统一顺序，否则会把旋转解释错。

### B6. 题目
> 为什么 `quaternion` 与 `-quaternion` 表示同一个旋转？比较两个四元数或插值前为什么需要处理符号？直接比较分量会有什么误判？

答案：

四元数对旋转是双覆盖，所以 `q` 和 `-q` 对应同一个 `SO(3)` 元素。

这意味着：

- 比较时不能直接按分量绝对值判断是否“相近”
- 插值前常要统一符号，避免路径突然绕远
- 直接比较会把同一旋转误判成完全不同的四元数

### B7. 题目
> 写出两个四元数的 Hamilton 乘积，并说明四元数乘法为什么不可交换，以及如何用单位四元数旋转三维向量。

答案：

设：

```text
q1 = [w1, v1]
q2 = [w2, v2]
```

则 Hamilton 乘积：

```text
q1 ⊗ q2 = [w1 w2 - v1·v2,
           w1 v2 + w2 v1 + v1 x v2]
```

四元数乘法不可交换，因为它对应的是旋转复合，而旋转复合本身就与顺序有关。

旋转向量常写成：

```text
p' = q ⊗ [0, p] ⊗ q^{-1}
```

### B8. 题目
> 比较旋转矩阵、欧拉角、轴角和单位四元数在参数量、约束、奇异性、复合效率、插值和可解释性方面的优缺点。机器人系统中哪些场景更适合用哪种表示？

答案：

- 旋转矩阵：无奇异，复合方便，适合计算，但参数多且有约束
- 欧拉角：最直观，适合人读写，但有奇异性
- 轴角：参数紧凑，几何意义清楚，适合小角度和增量
- 四元数：适合插值和连续优化，但有单位约束和双覆盖

常见选择：

- 机器人内部计算：旋转矩阵或四元数
- 日志、配置文件、人类查看：欧拉角
- 局部增量、优化：轴角或李代数

## C. SE(3) 与齐次变换

### C1. 题目
> `SO(3)` 和 `SE(3)` 分别表示什么？为什么三维刚体位姿不仅需要旋转，还需要平移？二者各有多少个自由度？

答案：

- `SO(3)`：三维旋转群
- `SE(3)`：三维刚体位姿群，包含旋转和平移

刚体位姿不仅有朝向，还有位置，所以需要平移。

自由度：

- `SO(3)`：3 个
- `SE(3)`：6 个

### C2. 题目
> 写出齐次变换矩阵 `T = [[R, translation], [0, 1]]`，说明各块的含义。为什么把三维点补成 `[x,y,z,1]^T` 后，旋转和平移可以统一成一次矩阵乘法？方向向量应补 `0` 还是 `1`？

答案：

齐次变换写作：

```text
T = [ R  t ]
    [ 0  1 ]
```

其中：

- `R`：旋转
- `t`：平移

把点写成 `[x,y,z,1]^T` 后，平移可以通过最后一列一起处理。

方向向量应补 `0`，因为方向不应该受平移影响。

### C3. 题目
> 坐标系 `{B}` 相对 `{A}` 绕 `z` 轴旋转 `90°`，且 `{B}` 原点在 `{A}` 中的位置为 `[1,2,0]^T`。构造 `T_ab`，并把 `{B}` 中的点 `[1,0,0]^T` 变换到 `{A}`。

答案：

旋转矩阵：

```text
R_ab = [ 0 -1  0 ]
       [ 1  0  0 ]
       [ 0  0  1 ]
```

齐次变换：

```text
T_ab = [ 0 -1  0  1 ]
       [ 1  0  0  2 ]
       [ 0  0  1  0 ]
       [ 0  0  0  1 ]
```

点变换结果：

```text
[1,0,0]^T -> [1,3,0]^T
```

计算过程就是：

```text
R_ab [1,0,0]^T + t_ab = [0,1,0]^T + [1,2,0]^T = [1,3,0]^T
```

### C4. 题目
> 从 `point_a = R_ab point_b + translation_ab` 推导 `T_ab^{-1}`，并解释为什么逆变换的平移部分不是简单的 `-translation_ab`。

答案：

逆变换为：

```text
T_ab^{-1} = [ R_ab^T   -R_ab^T translation_ab ]
            [   0                 1           ]
```

不是简单 `-t` 的原因是：

- 平移向量也要换到逆方向的坐标系里
- 逆变换不是只把数值取负，还要先经过旋转转回去

### C5. 题目
> 已知 `T_world_base`、`T_base_camera` 和相机系中的点 `point_camera`，写出 `point_world`。如果交换变换矩阵乘法顺序，几何意义会发生什么变化？这和 ROS 2 的 TF 树有什么联系？

答案：

```text
point_world = T_world_base T_base_camera point_camera
```

矩阵顺序一变，表示的坐标系链路就变了，结果会对应完全不同的几何关系。

TF 树本质上就是一棵坐标变换树，必须沿着父子关系依次组合变换。

### C6. 题目
> 为什么多个旋转矩阵不能直接逐元素平均后当作旋转矩阵？欧拉角跨越 `±pi` 时直接求均值为什么会出错？请给出至少一种更合理的旋转平均思路。

答案：

旋转矩阵属于流形，不是普通向量空间。  
逐元素平均后，结果通常不再满足正交性和 `det=1`。

欧拉角在跨越 `±pi` 时会出现周期性跳变，直接平均容易把两个“接近”的角度平均成一个错误方向。

更合理的方法：

- 四元数平均后再归一化
- 在李代数中做 `Log` / `Exp` 平均
- 先平均再用 SVD 投影回 `SO(3)`

## D. 李群、李代数与 exp/log

### D1. 题目
> 结合旋转或位姿变换，解释群的封闭性、结合律、单位元和逆元。为什么 `SO(3)` 和 `SE(3)` 被称为李群？

答案：

群需要满足：

- 封闭性：两个群元素做群运算后仍在群内
- 结合律：运算顺序可按结合律重组
- 单位元：存在不改变元素的单位对象
- 逆元：每个元素都有可逆元素

`SO(3)` 和 `SE(3)` 之所以是李群，是因为它们既满足群结构，又在局部可以当作光滑流形处理，可以做微分、指数映射和对数映射。

### D2. 题目
> `so(3)` 中的元素是什么形式？写出三维向量与反对称矩阵之间的 hat、vee 映射，并解释 `so(3)` 为什么可以看作 `SO(3)` 在单位元附近的切空间。

答案：

`so(3)` 的元素是 3x3 反对称矩阵：

```text
[omega]_x = [  0   -wz   wy ]
            [  wz    0   -wx ]
            [ -wy   wx    0  ]
```

`hat` 把向量变成反对称矩阵，`vee` 反过来：

```text
omega  <->  [omega]_x
```

`so(3)` 可以看作 `SO(3)` 在单位元附近的切空间，因为小旋转时旋转矩阵可近似展开为：

```text
R ≈ I + [omega]_x
```

### D3. 题目
> 从矩阵指数 `R = Exp([rotation_vector]_x)` 出发，说明旋转向量的方向和模长分别代表什么，并解释它与 Rodrigues 公式的关系。旋转向量接近零时，为什么要做小角度展开？

答案：

旋转向量 `rotation_vector = theta * u` 中：

- 方向 `u`：旋转轴方向
- 模长 `theta`：旋转角度

指数映射和 Rodrigues 公式描述的是同一件事：

```text
R = I + sin(theta)[u]_x + (1-cos(theta))[u]_x^2
```

当 `theta` 很小时，直接算 `sin(theta)/theta`、`(1-cos(theta))/theta^2` 容易数值不稳定，所以通常用泰勒展开近似。

### D4. 题目
> 对给定旋转矩阵 `R`，写出由 `trace(R)` 求旋转角的关系，并说明 `Log(R)` 返回什么。为什么旋转角接近 `0` 或 `pi` 时需要特殊处理？

答案：

常见关系：

```text
theta = arccos((trace(R)-1)/2)
```

`Log(R)` 的作用是把旋转矩阵映射回旋转向量或李代数元素。

需要特殊处理的原因：

- 接近 `0` 时，数值精度差，反对称项很小
- 接近 `pi` 时，轴的方向不唯一，且容易受到浮点误差影响

### D5. 题目
> 一个刚体 twist 通常由角速度部分和线速度部分组成。写出六维 twist 的矩阵形式，并说明它与 `se(3)` 的关系。注意说明你采用 `[omega, velocity]` 还是 `[velocity, omega]` 排列。

答案：

常见写法是：

```text
xi = [omega, v]

hat(xi) = [ [omega]_x  v ]
          [    0       0 ]
```

其中：

- `omega`：角速度部分
- `v`：线速度部分

`se(3)` 是 `SE(3)` 在单位元附近的切空间，对应刚体运动的局部增量。

### D6. 题目
> 说明 `Exp: se(3) -> SE(3)` 和 `Log: SE(3) -> se(3)` 的输入、输出及直观意义。它们为什么适合用于位姿插值、优化增量和误差定义？

答案：

- `Exp`：把李代数中的局部增量映射到刚体变换
- `Log`：把刚体变换拉回局部切空间

直观上：

- `Exp` 是“从小步变化走回真实位姿”
- `Log` 是“把两个位姿的差异压缩成局部误差”

它们适合插值和优化，因为局部空间更接近平直，便于线性化。

更完整地说，SE(3) 的指数映射里会出现旋转相关矩阵 `V`：

```text
T = [ R  Vv ]
    [ 0   1 ]
```

### D7. 题目
> 给定估计位姿 `T_estimated` 和目标位姿 `T_target`，可以构造左误差或右误差。任选一种，写出相对变换以及通过 `Log` 得到六维误差的过程，并解释误差表达在哪个坐标系中。

答案：

一种常见左误差写法：

```text
T_err = T_target^{-1} T_estimated
e = Log(T_err)
```

这里的误差表达在目标位姿对应的切空间附近。  
如果采用右误差，则坐标系解释会不同，但只要整套约定一致即可。

### D8. 题目
> 逐项判断并修正：1. 旋转向量就是欧拉角；2. 任意 `3 x 3` 矩阵都是旋转矩阵；3. 四元数只要有四个分量就能表示合法旋转；4. 位姿变换矩阵可以像普通向量一样相加；5. `Log(Exp(twist))` 对任意大小的 twist 都唯一等于原 twist。

答案：

1. 错，旋转向量不是欧拉角
2. 错，旋转矩阵必须满足正交和行列式约束
3. 错，四元数还要满足单位范数
4. 错，位姿不能直接按普通向量相加
5. 错，只在局部主值范围内才可视作对应

## E. NumPy 代码训练题

### E1. 题目
> 补全 `skew`、`project_to_so3`、`is_rotation_matrix` 三个函数，并验证旋转矩阵的正交性、行列式和逆矩阵关系。

答案：

下面的实现约定：输入必须是有限数值；`skew` 和 `project_to_so3` 对非法输入抛出
`ValueError`；`is_rotation_matrix` 是谓词，形状错误或非有限输入返回 `False`。

```python
import numpy as np


def _as_float_array(value, shape, name):
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain numeric values") from exc

    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def skew(vector):
    """输入 shape=(3,)，返回 3x3 反对称矩阵。"""
    v = _as_float_array(vector, (3,), "vector")
    return np.array([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0],
    ])


def project_to_so3(matrix):
    """使用 SVD 将有限 3x3 矩阵投影到 SO(3)。"""
    matrix = _as_float_array(matrix, (3, 3), "matrix")
    u, _, vt = np.linalg.svd(matrix)
    rotation = u @ vt

    # U @ Vt 可能是反射矩阵，翻转最后一个奇异方向使 det=+1。
    if np.linalg.det(rotation) < 0.0:
        u[:, -1] *= -1.0
        rotation = u @ vt
    return rotation


def is_rotation_matrix(matrix, atol=1e-9):
    """检查输入是否为有限的 SO(3) 矩阵。"""
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be a finite non-negative number")

    try:
        matrix = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError):
        return False

    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        return False

    orthogonality_error = np.max(
        np.abs(matrix.T @ matrix - np.eye(3))
    )
    determinant_error = abs(np.linalg.det(matrix) - 1.0)
    return bool(
        orthogonality_error <= atol
        and determinant_error <= atol
    )
```

参考实现要点：

- `skew(vector)`：返回 3x3 反对称矩阵
- `project_to_so3(matrix)`：对接近旋转矩阵的 3x3 矩阵做 SVD 投影
- `is_rotation_matrix(matrix)`：检查形状、有限性、正交性和 `det`

`project_to_so3` 的核心推导是：

```text
U, _, Vt = svd(M)
R = U @ Vt
```

`U @ Vt` 首先保证正交，但它可能是 `det=-1` 的反射矩阵；这时翻转
`U` 的最后一列，再重新计算 `R`，即可保证结果落在 `SO(3)`。

测试示例：

```python
rng = np.random.default_rng(42)
max_orthogonality_error = 0.0
max_determinant_error = 0.0
max_inverse_error = 0.0

for _ in range(1000):
    rotation = project_to_so3(rng.normal(size=(3, 3)))
    noisy = rotation + 1e-3 * rng.normal(size=(3, 3))
    projected = project_to_so3(noisy)

    for candidate in (rotation, projected):
        max_orthogonality_error = max(
            max_orthogonality_error,
            np.max(np.abs(candidate.T @ candidate - np.eye(3))),
        )
        max_determinant_error = max(
            max_determinant_error,
            abs(np.linalg.det(candidate) - 1.0),
        )
        max_inverse_error = max(
            max_inverse_error,
            np.max(np.abs(np.linalg.inv(candidate) - candidate.T)),
        )

assert np.allclose(skew([1.0, 2.0, 3.0]).T, -skew([1.0, 2.0, 3.0]))
assert is_rotation_matrix(projected)
assert not is_rotation_matrix(np.zeros((2, 2)))
assert not is_rotation_matrix(
    [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, np.nan]]
)

print(max_orthogonality_error)
print(max_determinant_error)
print(max_inverse_error)
```

在浮点误差范围内，三项最大误差都应接近 `1e-15` 到 `1e-14`；
具体数值取决于 NumPy 版本和平台。验证重点不是某个固定小数，而是：
`R.T @ R` 接近单位阵、`det(R)` 接近 `1`，并且
`inv(R)` 接近 `R.T`。

### E2. 题目
> 补全 `axis_angle_to_matrix`、`matrix_to_axis_angle`、`quaternion_to_matrix`、`matrix_to_quaternion` 四个函数，并说明你使用的四元数顺序。要求测试 `0`、接近 `pi` 和一般随机姿态。

答案：

下面统一采用四元数顺序 `[w, x, y, z]`，并把矩阵转轴角时的角度规范到
`[0, pi]`。四元数存在双覆盖：`q` 和 `-q` 表示同一个旋转，因此测试
四元数往返时不能直接比较四个分量。

```python
import numpy as np

EPS = 1e-12


def axis_angle_to_matrix(axis, angle):
    axis = np.asarray(axis, dtype=float)
    if axis.shape != (3,) or not np.all(np.isfinite(axis)):
        raise ValueError("axis must be a finite vector with shape (3,)")
    if not np.isfinite(angle):
        raise ValueError("angle must be finite")

    norm = np.linalg.norm(axis)
    if norm <= EPS:
        raise ValueError("axis must be non-zero")
    axis = axis / norm

    K = np.array([
        [0.0, -axis[2], axis[1]],
        [axis[2], 0.0, -axis[0]],
        [-axis[1], axis[0], 0.0],
    ])
    return np.eye(3) + np.sin(angle) * K + (1.0 - np.cos(angle)) * (K @ K)


def _check_rotation_matrix(matrix):
    matrix = np.asarray(matrix, dtype=float)
    if (
        matrix.shape != (3, 3)
        or not np.all(np.isfinite(matrix))
        or not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-8)
        or not np.isclose(np.linalg.det(matrix), 1.0, atol=1e-8)
    ):
        raise ValueError("matrix must be a valid SO(3) matrix")
    return matrix


def matrix_to_axis_angle(matrix):
    R = _check_rotation_matrix(matrix)
    cos_theta = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    skew_vector = np.array([
        R[2, 1] - R[1, 2],
        R[0, 2] - R[2, 0],
        R[1, 0] - R[0, 1],
    ])
    sin_theta = 0.5 * np.linalg.norm(skew_vector)
    # atan2 比 arccos 更能保留接近 0 的小角度信息。
    theta = float(np.arctan2(sin_theta, cos_theta))

    if theta <= EPS:
        # theta=0 时旋转轴没有唯一性，任选单位轴即可。
        return np.array([1.0, 0.0, 0.0]), 0.0

    if np.pi - theta <= 1e-7:
        # 接近 pi 时 sin(theta) 很小，不能直接除反对称部分。
        diagonal = np.maximum((np.diag(R) + 1.0) / 2.0, 0.0)
        i = int(np.argmax(diagonal))
        axis = np.zeros(3)
        axis[i] = np.sqrt(diagonal[i])
        for j in range(3):
            if j != i:
                axis[j] = (R[i, j] + R[j, i]) / (4.0 * axis[i])
        return axis / np.linalg.norm(axis), theta

    axis = skew_vector / (2.0 * np.sin(theta))
    return axis / np.linalg.norm(axis), theta


def quaternion_to_matrix(quaternion):
    q = np.asarray(quaternion, dtype=float)
    if q.shape != (4,) or not np.all(np.isfinite(q)):
        raise ValueError("quaternion must be a finite vector with shape (4,)")
    norm = np.linalg.norm(q)
    if norm <= EPS:
        raise ValueError("quaternion must be non-zero")

    w, x, y, z = q / norm
    return np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
        [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
        [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)],
    ])


def matrix_to_quaternion(matrix):
    R = _check_rotation_matrix(matrix)
    trace = np.trace(R)

    # 按 trace 或最大对角元素分支，避免接近 pi 时数值不稳定。
    if trace > 0.0:
        s = 2.0 * np.sqrt(trace + 1.0)
        q = np.array([
            0.25 * s,
            (R[2, 1] - R[1, 2]) / s,
            (R[0, 2] - R[2, 0]) / s,
            (R[1, 0] - R[0, 1]) / s,
        ])
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        q = np.array([
            (R[2, 1] - R[1, 2]) / s,
            0.25 * s,
            (R[0, 1] + R[1, 0]) / s,
            (R[0, 2] + R[2, 0]) / s,
        ])
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        q = np.array([
            (R[0, 2] - R[2, 0]) / s,
            (R[0, 1] + R[1, 0]) / s,
            0.25 * s,
            (R[1, 2] + R[2, 1]) / s,
        ])
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        q = np.array([
            (R[1, 0] - R[0, 1]) / s,
            (R[0, 2] + R[2, 0]) / s,
            (R[1, 2] + R[2, 1]) / s,
            0.25 * s,
        ])

    q /= np.linalg.norm(q)
    # 固定 q[0] >= 0，便于日志和数值比较；这不改变旋转。
    return q if q[0] >= 0.0 else -q
```

核心关系：

- 轴角转矩阵：先归一化旋转轴，再用 Rodrigues 公式；
- 矩阵转轴角：用 `trace` 求角度，再从反对称部分恢复轴；
- 四元数转矩阵：先归一化，再按 `[w, x, y, z]` 展开；
- 矩阵转四元数：按 `trace` 或最大对角元素分支，避免数值不稳定。

测试旋转误差时使用：

```python
def rotation_error(R1, R2):
    relative = R1.T @ R2
    cosine = np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0)
    sine = 0.5 * np.linalg.norm([
        relative[2, 1] - relative[1, 2],
        relative[0, 2] - relative[2, 0],
        relative[1, 0] - relative[0, 1],
    ])
    return np.arctan2(sine, cosine)
```

固定随机种子测试至少 `1000` 次，并覆盖 `angle=0`、接近 `pi` 和一般角度。
四元数往返时可以比较旋转矩阵误差，或者比较
`abs(np.dot(q1, q2))` 是否接近 `1`，不能直接要求 `q1 == q2`。

### E3. 题目
> 实现 `make_transform`、`inverse_transform`、`transform_points` 和 `compose_transforms`，要求支持单点和批量点，并验证逆变换和复合变换的一致性。

答案：

下面采用列向量约定：

```text
p_a = T_ab p_b
T_ab：把 {B} 坐标中的点变换到 {A}
T_ac = T_ab @ T_bc
```

因此齐次变换写成：

```text
T = [[R, t],
     [0, 1]]
```

其中 `R` 是 `SO(3)` 旋转矩阵，`t` 是平移向量。

完整实现如下：

```python
import numpy as np


def make_transform(rotation, translation):
    rotation = np.asarray(rotation, dtype=float)
    translation = np.asarray(translation, dtype=float)
    if rotation.shape != (3, 3):
        raise ValueError("rotation must have shape (3, 3)")
    if translation.shape != (3,):
        raise ValueError("translation must have shape (3,)")
    if not np.all(np.isfinite(rotation)):
        raise ValueError("rotation must be finite")
    if not np.all(np.isfinite(translation)):
        raise ValueError("translation must be finite")
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-8):
        raise ValueError("rotation must be orthogonal")
    if not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-8):
        raise ValueError("rotation must have determinant +1")

    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation
    return T


def _validate_transform(transform):
    T = np.asarray(transform, dtype=float)
    if T.shape != (4, 4) or not np.all(np.isfinite(T)):
        raise ValueError("transform must be a finite 4x4 matrix")
    if not np.allclose(T[:3, :3].T @ T[:3, :3], np.eye(3), atol=1e-8):
        raise ValueError("transform rotation block is invalid")
    if not np.isclose(np.linalg.det(T[:3, :3]), 1.0, atol=1e-8):
        raise ValueError("transform rotation block must have determinant +1")
    if not np.allclose(T[3], [0.0, 0.0, 0.0, 1.0], atol=1e-8):
        raise ValueError("invalid homogeneous bottom row")
    return T


def inverse_transform(transform):
    T = _validate_transform(transform)
    R = T[:3, :3]
    t = T[:3, 3]

    T_inverse = np.eye(4)
    T_inverse[:3, :3] = R.T
    T_inverse[:3, 3] = -R.T @ t
    return T_inverse


def transform_points(transform, points):
    T = _validate_transform(transform)
    points = np.asarray(points, dtype=float)
    if not np.all(np.isfinite(points)):
        raise ValueError("points must be finite")

    R = T[:3, :3]
    t = T[:3, 3]
    if points.shape == (3,):
        return R @ points + t
    if points.ndim == 2 and points.shape[1] == 3:
        return points @ R.T + t
    raise ValueError("points must have shape (3,) or (N, 3)")


def compose_transforms(transform_ab, transform_bc):
    T_ab = _validate_transform(transform_ab)
    T_bc = _validate_transform(transform_bc)
    return T_ab @ T_bc
```

逆变换的推导是：

```text
p_a = R_ab p_b + t_ab
p_b = R_ab^T (p_a - t_ab)
    = R_ab^T p_a - R_ab^T t_ab
```

所以：

```text
T_ab^-1 = [[R_ab^T, -R_ab^T t_ab],
           [0,       1          ]]
```

测试时至少要验证：

```python
identity = np.eye(4)
assert np.allclose(T @ inverse_transform(T), identity)
assert np.allclose(inverse_transform(T) @ T, identity)

single = transform_points(T, point)
batch = transform_points(T, point.reshape(1, 3))[0]
assert np.allclose(single, batch)

sequential = transform_points(
    T_ab,
    transform_points(T_bc, points),
)
composed = transform_points(
    compose_transforms(T_ab, T_bc),
    points,
)
assert np.allclose(sequential, composed)
```

固定随机种子运行至少 `1000` 次，并记录：

- `T @ T^{-1}` 的最大绝对矩阵误差；
- 单点与批量点结果的最大绝对误差；
- 连续变换与复合变换结果的最大绝对误差；
- 点经过变换再经过逆变换后的最大绝对误差。

### E4. 题目
> 使用自己的函数或可靠库完成 `so3_exp`、`so3_log`，并画出误差随旋转角变化的曲线。说明哪些角度附近误差会变大，以及为什么。

答案：

约定旋转向量 `phi` 的方向是旋转轴，模长是旋转角：

```text
phi = theta * axis
```

完整实现如下：

```python
import numpy as np

EPS = 1e-12


def skew(vector):
    x, y, z = vector
    return np.array([
        [0.0, -z, y],
        [z, 0.0, -x],
        [-y, x, 0.0],
    ])


def so3_exp(rotation_vector):
    phi = np.asarray(rotation_vector, dtype=float)
    if phi.shape != (3,) or not np.all(np.isfinite(phi)):
        raise ValueError("rotation_vector must be a finite vector with shape (3,)")

    theta = np.linalg.norm(phi)
    Phi = skew(phi)

    if theta < 1e-4:
        theta2 = theta * theta
        A = 1.0 - theta2 / 6.0 + theta2 * theta2 / 120.0
        B = 0.5 - theta2 / 24.0 + theta2 * theta2 / 720.0
    else:
        A = np.sin(theta) / theta
        B = (1.0 - np.cos(theta)) / (theta * theta)

    return np.eye(3) + A * Phi + B * (Phi @ Phi)


def _axis_near_pi(R):
    diagonal = np.maximum((np.diag(R) + 1.0) / 2.0, 0.0)
    i = int(np.argmax(diagonal))
    axis = np.zeros(3)
    axis[i] = np.sqrt(diagonal[i])

    for j in range(3):
        if j != i:
            axis[j] = (R[i, j] + R[j, i]) / (4.0 * axis[i])
    return axis / np.linalg.norm(axis)


def so3_log(rotation):
    R = np.asarray(rotation, dtype=float)
    if (
        R.shape != (3, 3)
        or not np.all(np.isfinite(R))
        or not np.allclose(R.T @ R, np.eye(3), atol=1e-8)
        or not np.isclose(np.linalg.det(R), 1.0, atol=1e-8)
    ):
        raise ValueError("rotation must be a valid SO(3) matrix")

    vee = np.array([
        R[2, 1] - R[1, 2],
        R[0, 2] - R[2, 0],
        R[1, 0] - R[0, 1],
    ])
    sin_theta = 0.5 * np.linalg.norm(vee)
    cos_theta = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    theta = np.arctan2(sin_theta, cos_theta)

    if theta < 1e-7:
        # R 接近 I 时，Log(R) vee 约等于 vee(R-R.T)/2。
        return 0.5 * vee

    if np.pi - theta < 1e-7:
        # 接近 pi 时 sin(theta) 接近 0，改从对角线恢复轴。
        return theta * _axis_near_pi(R)

    axis = vee / (2.0 * np.sin(theta))
    return theta * axis
```

`so3_exp` 的公式来自 Rodrigues 展开：

```text
Exp(phi^) = I
          + sin(theta)/theta * phi^
          + (1-cos(theta))/theta^2 * (phi^)^2
```

当 `theta` 接近 `0` 时，直接计算两个系数会有除零或消去误差，
所以使用 Taylor 展开：

```text
sin(theta)/theta       ≈ 1 - theta^2/6 + theta^4/120
(1-cos(theta))/theta²  ≈ 1/2 - theta²/24 + theta^4/720
```

`so3_log` 先由：

```text
cos(theta) = (trace(R) - 1) / 2
sin(theta) = ||vee(R - R^T)|| / 2
```

使用 `atan2(sin(theta), cos(theta))` 求主值角度，再恢复旋转轴。
相比直接使用 `arccos`，`atan2` 在零角附近更稳定。

接近 `pi` 时，`sin(theta)` 接近零，反对称部分几乎没有信息，
此时使用：

```text
axis_i^2 = (R_ii + 1) / 2
```

从最大的对角元素开始恢复轴，避免除以接近零的数。

测试代码：

```python
def rotation_error(R1, R2):
    relative = R1.T @ R2
    vee = np.array([
        relative[2, 1] - relative[1, 2],
        relative[0, 2] - relative[2, 0],
        relative[1, 0] - relative[0, 1],
    ])
    sin_theta = 0.5 * np.linalg.norm(vee)
    cos_theta = np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0)
    return np.arctan2(sin_theta, cos_theta)


rng = np.random.default_rng(42)
max_exp_log_error = 0.0

for _ in range(1000):
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    theta = rng.uniform(0.0, np.pi)
    phi = theta * axis

    R = so3_exp(phi)
    phi_recovered = so3_log(R)
    R_recovered = so3_exp(phi_recovered)
    max_exp_log_error = max(
        max_exp_log_error,
        rotation_error(R, R_recovered),
    )

print(max_exp_log_error)
```

还需要单独测试 `theta=0`、接近 `0`、接近 `pi` 和正好 `pi`。
如果测试 `Log(Exp(phi))` 的旋转向量本身，必须注意主值范围：
通常 `Log` 返回角度在 `[0, pi]`，因此当 `||phi|| > pi` 时，
返回向量可能变成相反轴、较小角度，但重新 `Exp` 后的旋转矩阵仍然相同。

误差通常在以下位置更敏感：

- `0` 附近：直接除以 `theta` 或使用 `arccos` 会损失精度；
- `pi` 附近：旋转轴符号不唯一，且反对称部分趋近于零；
- `pi` 之外：对数映射使用主值，旋转向量表示会发生分支切换。

### E5. 题目
> 使用 Matplotlib 画出世界坐标系、两个子坐标系和一个点变换前后的结果，要求同时用图和数值验证复合顺序。

答案：

采用列向量约定：

```text
p_a = T_ab p_b
p_w = T_wa p_a
T_wb = T_wa @ T_ab
```

其中：

- `T_wa` 把 `{A}` 中的坐标变换到 `{W}`；
- `T_ab` 把 `{B}` 中的坐标变换到 `{A}`；
- `T_wb` 把 `{B}` 中的坐标直接变换到 `{W}`。

完整实验代码如下：

```python
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def draw_frame(ax, T, name, length=0.45):
    origin = T[:3, 3]
    rotation = T[:3, :3]
    colors = ["tab:red", "tab:green", "tab:blue"]
    labels = ["x", "y", "z"]

    ax.scatter(*origin, color="black", s=24)
    ax.text(*origin, f"  {name}")
    for i, (color, label) in enumerate(zip(colors, labels)):
        direction = length * rotation[:, i]
        ax.quiver(
            *origin,
            *direction,
            color=color,
            linewidth=2.0,
            arrow_length_ratio=0.18,
        )
        ax.text(*(origin + direction), f"{label}_{name}", color=color)


rng = np.random.default_rng(42)

# T_wa: A -> W, T_ab: B -> A
T_wa = make_transform(
    so3_exp(rng.normal(size=3)),
    rng.uniform(-1.0, 1.0, size=3),
)
T_ab = make_transform(
    so3_exp(rng.normal(size=3)),
    rng.uniform(-1.0, 1.0, size=3),
)
T_wb = T_wa @ T_ab

p_b = rng.uniform(-0.6, 0.6, size=3)
p_a = transform_points(T_ab, p_b)
p_w_step = transform_points(T_wa, p_a)
p_w_direct = transform_points(T_wb, p_b)

assert np.allclose(p_w_step, p_w_direct)

# 矩阵乘法通常不交换；反向相乘只作为数值对照，不能解释为同一条变换链。
wrong_order = T_ab @ T_wa
noncommutativity_error = np.max(np.abs(T_wb - wrong_order))
assert noncommutativity_error > 1e-8

figure = plt.figure(figsize=(9, 7))
ax = figure.add_subplot(111, projection="3d")
draw_frame(ax, np.eye(4), "W")
draw_frame(ax, T_wa, "A")
draw_frame(ax, T_wb, "B")

ax.scatter(*p_w_direct, color="darkorange", s=70, label="same point in W")
ax.text(
    *p_w_direct,
    "  p_W=" + np.array2string(p_w_direct, precision=2),
    color="darkorange",
)

ax.text2D(
    0.02,
    0.97,
    "p_B = " + np.array2string(p_b, precision=3) + "\n"
    "p_A = " + np.array2string(p_a, precision=3) + "\n"
    "p_W = " + np.array2string(p_w_direct, precision=3) + "\n"
    f"chain error = {np.max(np.abs(p_w_step - p_w_direct)):.2e}\n"
    f"wrong-order diff = {noncommutativity_error:.2e}",
    transform=ax.transAxes,
    verticalalignment="top",
    family="monospace",
    bbox={"facecolor": "white", "alpha": 0.8},
)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("SE(3) coordinate transform: B -> A -> W")
ax.legend()
figure.tight_layout()
figure.savefig("e5-coordinate-transforms.png", dpi=160)
plt.close(figure)

parameters = {
    "seed": 42,
    "T_wa": T_wa.tolist(),
    "T_ab": T_ab.tolist(),
    "T_wb": T_wb.tolist(),
    "p_b": p_b.tolist(),
    "p_a": p_a.tolist(),
    "p_w": p_w_direct.tolist(),
    "chain_max_abs_error": float(np.max(np.abs(p_w_step - p_w_direct))),
    "noncommutativity_max_abs_difference": float(noncommutativity_error),
}
Path("e5-coordinate-transforms.json").write_text(
    json.dumps(parameters, indent=2),
    encoding="utf-8",
)
```

图中应包含：

- 世界坐标系 `{W}`；
- 两个子坐标系 `{A}`、`{B}`；
- 每个坐标系的红、绿、蓝三根轴；
- 点在 `{B}`、`{A}`、`{W}` 中的坐标；
- 两级变换链的数值误差。

验收时检查：

```text
max_abs(p_w_step - p_w_direct) 接近 0
max_abs(T_wa @ T_ab - T_ab @ T_wa) 明显大于 0
```

第一个结果说明复合顺序和图中的点位置一致；第二个结果说明
刚体变换的矩阵乘法一般不满足交换律，不能随意调换变换顺序。

### E6. 题目
> 固定 yaw 和 roll，让 `ZYX` 欧拉角中的 pitch 从 `80°` 变化到 `100°`。把欧拉角转成旋转矩阵后再转回，记录恢复出的三个角度，并解释为什么会出现跳变。

答案：

采用主动旋转和 `ZYX` 顺序：

```text
R(yaw, pitch, roll) = Rz(yaw) Ry(pitch) Rx(roll)
```

固定：

```text
yaw = 35°
roll = -25°
pitch: 80° -> 100°
```

欧拉角转旋转矩阵：

```python
import numpy as np


def Rx(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, c, -s],
        [0.0, s, c],
    ])


def Ry(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [c, 0.0, s],
        [0.0, 1.0, 0.0],
        [-s, 0.0, c],
    ])


def Rz(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ])


def euler_zyx_to_matrix(yaw, pitch, roll):
    return Rz(yaw) @ Ry(pitch) @ Rx(roll)
```

一般情况下，从矩阵恢复 `ZYX` 欧拉角：

```python
def matrix_to_euler_zyx(R, singularity_tolerance=1e-10):
    sine_pitch = np.clip(-R[2, 0], -1.0, 1.0)
    pitch = np.arcsin(sine_pitch)
    cosine_pitch = np.sqrt(max(0.0, 1.0 - sine_pitch**2))

    if cosine_pitch > singularity_tolerance:
        yaw = np.arctan2(R[1, 0], R[0, 0])
        roll = np.arctan2(R[2, 1], R[2, 2])
    else:
        # pitch=+/-90° 时 yaw 与 roll 耦合，无法分别唯一确定。
        yaw = 0.0
        if sine_pitch > 0.0:
            roll = np.arctan2(R[0, 1], R[0, 2])
        else:
            roll = np.arctan2(-R[0, 1], -R[0, 2])
    return yaw, pitch, roll
```

实验循环：

```python
pitch_values = np.deg2rad(np.linspace(80.0, 100.0, 401))
yaw = np.deg2rad(35.0)
roll = np.deg2rad(-25.0)

matrices = np.array([
    euler_zyx_to_matrix(yaw, pitch, roll)
    for pitch in pitch_values
])
recovered = np.array([
    matrix_to_euler_zyx(R)
    for R in matrices
])

matrix_step_error = np.max(
    np.abs(np.diff(matrices, axis=0)),
    axis=(1, 2),
)
reconstructed = np.array([
    euler_zyx_to_matrix(yaw_i, pitch_i, roll_i)
    for yaw_i, pitch_i, roll_i in recovered
])
reconstruction_error = np.max(
    np.abs(matrices - reconstructed),
    axis=(1, 2),
)
```

画图时应同时显示：

1. 输入 yaw、pitch、roll；
2. 从矩阵恢复出的 yaw、pitch、roll；
3. 相邻旋转矩阵的最大差异；
4. 用恢复欧拉角重建矩阵的误差。

现象与解释：

- 输入 pitch 从 `80°` 连续增加到 `100°`；
- 恢复出的 pitch 通常被限制在 `[-90°, 90°]`；
- 穿过 `90°` 后，恢复出的 yaw 和 roll 会跳到另一组等价角度；
- 原始旋转矩阵仍然连续，且重建误差接近浮点误差；
- 在正好 `pitch=90°` 时，yaw 和 roll 的两个自由度合并，只能观察到它们的某种组合。

因此 gimbal lock 不是刚体真的丢失了一个物理自由度，而是
`ZYX` 欧拉角参数化在 `pitch=±90°` 处退化。工程上应避免直接对欧拉角做插值
或控制误差，优先使用旋转矩阵、四元数或李代数增量。

影响包括：

- 姿态插值：欧拉角可能突然跳变，导致插值路径错误；
- 控制器：角度误差可能出现很大的假跳变；
- 日志分析：角度曲线不连续，但旋转矩阵曲线仍连续；
- 调试：必须同时检查旋转矩阵误差，不能只看欧拉角分量。

## F. 应用与理解

### F1. 题目
> 机器人基座、末端执行器、相机和目标物体各自有坐标系。请设计一条从相机观测目标位姿到基座系目标位姿的变换链，并说明每个变换应通过标定、运动学还是感知获得。

答案：

一条常见链路是：

```text
T_world_target = T_world_base T_base_camera T_camera_target
```

通常：

- 标定获得外参
- 运动学提供机器人链条上的位姿
- 感知提供相机中目标的位姿

### F2. 题目
> 分别为以下场景选择旋转或位姿表示，并解释原因：网络输出一个物体朝向；配置文件记录人类可读姿态；连续平滑插值两个朝向；优化器中的小位姿增量；TF 树中传播完整刚体位姿。

答案：

1. 网络输出朝向：四元数或旋转矩阵
2. 配置文件记录姿态：欧拉角
3. 连续平滑插值：四元数
4. 小位姿增量：李代数增量
5. TF 树传播位姿：齐次矩阵或四元数 + 平移

### F3. 题目
> 当变换后的点位置明显错误时，给出一套排查顺序，至少覆盖：坐标系命名、变换方向、乘法顺序、角度单位、欧拉角顺序、四元数分量顺序、矩阵存储约定和时间戳。

答案：

推荐排查顺序：

- 坐标系命名
- 变换方向
- 乘法顺序
- 角度单位
- 欧拉角顺序
- 四元数分量顺序
- 矩阵存储约定
- 时间戳是否对齐

### F4. 题目
> “随机测试误差达到数值精度”具体应该如何定义？为什么只测单位矩阵或少量手工样例不够？说明你会记录哪些误差指标、边界样例和失败样例。

答案：

“达到数值精度”一般不是指某一次样例刚好过了，而是指：

- 在足够多随机样例下
- 最大误差、平均误差都小于预设阈值
- 边界样例也能稳定通过

建议记录：

- 随机种子
- 最大误差
- 平均误差
- 边界样例
- 失败样例

## G. 本周验收

完成本文件和代码实验后，可以用下面几句自测：

1. 我能解释 `SO(3)`、`SE(3)`、`so(3)` 和 `se(3)` 的区别与联系。
2. 我能独立写出并检查一条位姿变换链。
3. 我能在旋转矩阵、欧拉角、轴角和四元数之间做可靠转换，并处理边界情况。
4. 我能解释 `gimbal lock` 是参数化奇异性，而不是刚体真的失去自由度。
5. 我能用随机测试验证实现，并记录误差阈值、随机种子和失败样例。
6. 我能画出多坐标系变换图，并让图和数值结果一致。
7. 我还需要继续补强的是 `SE(3)` 的 `Log` 在接近 `pi`、以及四元数双覆盖下的处理细节。
