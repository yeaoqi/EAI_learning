# Week 01 Lab: Least Squares and SVD

这个实验用于观察三件事：

- 最小二乘如何拟合带噪声的直线 `y = 2x + 1`
- `np.linalg.lstsq` 和手动 SVD 解法是否一致
- 当矩阵病态时，奇异值和条件数会如何变化

## 运行

```bash
python labs/week1-svd/least_squares_svd.py
```

## 观察重点

正常数据中，`theta_lstsq` 和 `theta_svd` 应该都接近：

```text
[2, 1]
```

病态数据中，`x` 的范围非常窄，矩阵两列接近线性相关。此时最小奇异值会很小，条件数会很大，斜率和截距可能变得非常夸张，但两种解法仍应基本一致。

## 复盘问题

- 为什么病态数据中斜率和截距会变得很大？
- 为什么 `theta_lstsq` 和 `theta_svd` 的结果应该接近？
- 条件数越大，说明这个拟合问题越稳定还是越不稳定？
