# 05 PyTorch 训练闭环参考答案

这份文件按 Week 5 自测题号给出参考答案。概念题可以用自己的话复述；代码题给出一套偏工程化的实现，重点是形状、dtype、device、统计方式、可复现性和错误检查。

## A. Tensor 与 autograd

### A1. Tensor、dtype、device 与 shape

`torch.Tensor` 和 NumPy 数组都可以保存多维数值，但 Tensor 额外支持：

- 自动求导：可以记录计算图并计算梯度；
- GPU/其他设备：数据和运算可以放在 `cuda` 等 device 上；
- 深度学习算子和 `nn.Module` 的参数管理；
- 与 PyTorch 的优化器、分布式训练和混合精度配合。

NumPy 数组主要面向 CPU 数值计算。CPU 上的 Tensor 和 NumPy 数组有时可以共享内存，例如 `torch.from_numpy(array)`，但共享内存并不意味着它们支持相同的 autograd 行为。

几个属性的含义：

- `dtype`：元素类型，例如 `torch.float32`、`torch.float16`、`torch.int64`。
- `device`：数据所在设备，例如 `cpu` 或 `cuda:0`。
- `shape`：每一维的长度，例如图像 batch 常见为 `(B, C, H, W)`。
- `stride`：沿每个维度移动一个索引时，底层存储位置跳过多少个元素。转置、切片后 Tensor 可能变成非 contiguous，但逻辑 `shape` 仍然可以不变。

模型参数和连续值输入通常使用浮点 dtype；分类标签传给 `CrossEntropyLoss` 时通常使用一维 `torch.long` Tensor。参与同一个算子的 Tensor 一般需要位于同一 device，形状也要满足算子的约束。否则会得到 device mismatch、dtype mismatch 或 shape mismatch 错误；即使广播成功，语义也可能是错的。

常用检查：

```python
print(images.shape, images.dtype, images.device, images.stride())
print(next(model.parameters()).dtype, next(model.parameters()).device)
print(labels.shape, labels.dtype, labels.device)
```

### A2. 广播与批量维度

矩阵乘法的结果形状为：

```text
(batch_size, feature_dim) @ (feature_dim, output_dim)
= (batch_size, output_dim)
```

`bias.shape == (output_dim,)` 可以看成 `(1, output_dim)`。加法时它沿 batch 维广播：

```text
(batch_size, output_dim)
+ (1, output_dim)
= (batch_size, output_dim)
```

按元素写就是：

```text
output[b, j] = sum_i input_batch[b, i] * weight[i, j] + bias[j]
```

广播成功不代表语义正确。例如图像为 `(B, 3, 32, 32)`，错误地加上形状 `(32,)` 的 Tensor 时，PyTorch 可能把它广播到最后一维：

```python
images = torch.randn(8, 3, 32, 32)
wrong_bias = torch.randn(32)
result = images + wrong_bias  # 能运行，但它给每个宽度位置加了不同值
```

如果想给每个通道加偏置，应使用 `(1, 3, 1, 1)`，而不是依赖“刚好能广播”：

```python
channel_bias = torch.randn(1, 3, 1, 1)
result = images + channel_bias
```

### A3. 叶子张量与计算图

Leaf Tensor 是计算图中由用户直接创建、而不是由其他 Tensor 运算产生的 Tensor。典型例子是：

```python
weight = torch.randn(3, 2, requires_grad=True)
```

它是 leaf，并且 `weight.grad` 默认会在反向传播后保存。`nn.Parameter` 是专门用于模块参数注册的 Tensor 子类；放进 `nn.Module` 属性后，会被 `model.parameters()` 找到。

四种情况：

1. **直接创建且需要梯度的参数**：通常是 leaf，`requires_grad=True`，反向后保存 `.grad`。
2. **对参数运算得到的中间 Tensor**：例如 `z = weight @ x`，它通常不是 leaf，有 `grad_fn`。默认不会保存自己的 `.grad`，除非调用 `z.retain_grad()`。
3. **`torch.no_grad()` 中得到的 Tensor**：这段计算不记录 autograd 图，结果通常 `requires_grad=False`，适合验证和推理。
4. **`detach()` 得到的 Tensor**：与原 Tensor 共享存储，但从当前计算图断开。对它继续计算不会把梯度传回原 Tensor。

`requires_grad=True` 的含义是：在梯度模式开启时，后续使用该 Tensor 的运算会被 autograd 记录，从而可以对它求导。它不是“立刻计算梯度”，也不会替代 `loss.backward()`。

### A4. 反向传播与链式法则

给定：

```text
z = weight * input + bias
loss = (z - target)^2 / 2
```

先求局部导数：

```text
d loss / d z = z - target
d z / d weight = input
d z / d input = weight
d z / d bias = 1
```

因此：

```text
d loss / d weight = (z - target) * input
d loss / d input  = (z - target) * weight
d loss / d bias   = z - target
```

如果 `weight`、`input`、`bias` 是向量或矩阵，乘法和加法应按对应元素或矩阵运算规则理解。`loss.backward()` 从标量 loss 开始，沿着 `grad_fn` 保存的计算图反向应用链式法则，并把结果累加到 leaf Tensor 的 `.grad`。

### A5. 梯度累积

PyTorch 默认累积梯度，是因为它支持梯度累积训练、多个 loss 相加、微批次模拟大 batch 等用法。因此一次 `backward()` 不会自动覆盖已有 `.grad`。

普通训练的伪代码：

```python
model.train()
for images, labels in data_loader:
    images = images.to(device)
    labels = labels.to(device)

    optimizer.zero_grad(set_to_none=True)
    logits = model(images)
    loss = loss_fn(logits, labels)
    loss.backward()
    optimizer.step()
```

清零可以放在每个 batch 的 `backward()` 之前。也可以在上一个 `optimizer.step()` 后清零，但必须保证每次反向前梯度状态符合预期。

如果忘记清零，第 `k` 个 batch 的梯度大致会变成前 `k` 个 batch 梯度之和。参数更新会越来越大，训练结果会依赖 batch 数，容易震荡、发散或产生错误的有效学习率。

### A6. `detach`、`no_grad` 与 `inference_mode`

| 方法 | 计算图 | 是否改变模型模式 | 常见用途 |
|---|---|---|---|
| `tensor.detach()` | 只断开这个 Tensor 的历史 | 不改变 | 将某个中间结果当作常量、转 NumPy |
| `torch.no_grad()` | 整个上下文不记录梯度 | 不改变 | 验证、普通推理、冻结部分计算 |
| `torch.inference_mode()` | 比 `no_grad` 更激进地关闭 autograd 相关开销 | 不改变 | 纯推理，通常更快，但对某些需要 autograd metadata 的操作限制更多 |

`eval()` 和这些上下文是两件事：`eval()` 影响 Dropout、BatchNorm 等模块的行为；`no_grad()`/`inference_mode()` 影响是否构建梯度图。

验证推荐：

```python
model.eval()
with torch.inference_mode():
    logits = model(images)
```

训练中的输出转 NumPy：

```python
values = model(images).detach().cpu().numpy()
```

如果整个循环都是推理，优先使用 `model.eval()` 加 `torch.inference_mode()`；如果还要继续对输出求梯度，就不能使用 `detach()` 或 `no_grad()`。

### A7. 自动求导的边界

- 参数没有参与当前 loss：它没有从 loss 到参数的路径，所以 `.grad` 可能保持为 `None`。这与“梯度存在但恰好为 0”不同。
- `.item()` 把单元素 Tensor 转成 Python 数字，计算图信息丢失。如果后续 loss 只由这个 Python 数字计算，梯度不会再回到原 Tensor。
- 原地修改需要梯度的 Tensor：可能覆盖 autograd 反向所需的旧值，触发 `one of the variables needed for gradient computation has been modified`。
- 在 `no_grad()` 中完成训练前向：loss 通常没有有效的计算图，调用 `backward()` 会报错或无法产生参数梯度。
- 对非标量 loss 直接调用 `backward()`：PyTorch 不知道要乘以哪个外部梯度，通常会报 `grad can be implicitly created only for scalar outputs`。应先 `loss.mean()`/`loss.sum()`，或显式传入同形状的梯度。

### A8. 小结

训练闭环的核心是：输入、参数、标签的 dtype/device/shape 先对齐；loss 是可反向传播的标量；每个 batch 在反向前清零梯度；验证时同时使用 `eval()` 和无梯度上下文。

## B. Dataset、DataLoader 与 Module

### B1. `Dataset` 接口

Map-style `Dataset` 通常实现：

```python
class ImageDataset(torch.utils.data.Dataset):
    def __len__(self):
        ...

    def __getitem__(self, index):
        ...
```

`__getitem__` 通常返回 `(image, label)`，也可以返回字典：

```python
{
    "image": image_tensor,       # (C, H, W), float32
    "label": label_tensor,       # scalar or int64
    "timestamp": timestamp,      # optional metadata
}
```

图像分类中，建议在 dataset/transform 阶段统一：

- 图像布局为 `(C, H, W)`；
- 图像 dtype 为 `float32`；
- 像素范围和归一化方式固定；
- 标签是从 `0` 到 `num_classes - 1` 的整数；
- 单样本不会带多余的 batch 维。

这样 DataLoader 只负责拼 batch，模型和 loss 可以获得稳定的输入约定，避免训练时某些 batch 是 `uint8`、某些 batch 是 float，或标签从 `1` 开始而 loss 期望从 `0` 开始。

### B2. `DataLoader` 参数

- `batch_size`：每个 batch 的样本数，影响显存、吞吐、梯度噪声和每个 epoch 的 step 数。
- `shuffle`：是否在每个 epoch 重新打乱索引。训练集通常为 `True`，验证集通常为 `False`。
- `drop_last`：是否丢弃最后一个不完整 batch。训练时有时为了稳定 BatchNorm 使用 `True`；验证统计通常应使用 `False`，避免丢失样本。
- `num_workers`：CPU worker 数量，主要影响数据准备吞吐，也会引入 worker 随机状态和进程开销。
- `pin_memory`：把 CPU batch 放入锁页内存，配合 CUDA 的 `non_blocking=True` 通常可以加快 Host-to-Device 拷贝。
- `persistent_workers`：跨 epoch 保留 worker，避免每个 epoch 重启进程；只有 `num_workers > 0` 时有意义。

`batch_size`、`num_workers`、`pin_memory` 主要影响吞吐和训练统计的细节；`shuffle`、`drop_last` 会改变样本顺序或参与训练的样本；worker 的随机增强也可能改变样本内容。验证集一般不需要 `shuffle=True`，因为不打乱更容易复现和定位样本，且不会改善总体指标。

### B3. 数据划分与泄漏

推荐流程：

1. 先确定测试集，只在最终报告使用。
2. 从训练部分固定划分 train/validation，保存索引或划分随机种子。
3. 只用 train 训练参数；用 validation 选择 epoch、学习率、增强和模型。
4. 完成方案后只在 test 上评估一次或极少次数。

不能用测试集选超参数，否则测试信息已经参与了模型选择，最终 test accuracy 会偏乐观。

CIFAR-10 中常见泄漏包括：

- 把 test 图片或其增强版本混进 train；
- 先对全体数据计算归一化均值/方差或数据增强统计，再划分；
- 同一张原图的近重复、裁剪版本同时出现在 train 和 validation；
- 用 test accuracy 选择 checkpoint 或早停 epoch；
- 先在全数据上做特征选择、类别统计或人工调参。

### B4. `nn.Module` 与参数注册

- `nn.Module`：模型和子模块的基类，负责递归管理参数、buffer、device、模式和 `state_dict`。
- `nn.Parameter`：放在 Module 属性中的可训练参数，会自动被注册。
- `ModuleList`：注册一组子模块，但不自动定义它们如何连接。
- `Sequential`：注册一组子模块，并按顺序调用。
- 普通 Python `list`：只是容器。把 `nn.Linear` 放进去时，Module 不知道这些层是子模块，`model.parameters()`、`to(device)`、`state_dict()` 可能找不到或不管理它们。

正确写法：

```python
self.layers = nn.ModuleList([
    nn.Linear(10, 32),
    nn.ReLU(),
    nn.Linear(32, 4),
])
```

或者：

```python
self.layers = nn.Sequential(
    nn.Linear(10, 32),
    nn.ReLU(),
    nn.Linear(32, 4),
)
```

### B5. `train()` 与 `eval()`

`model.train()` 将模块切换到训练模式，`model.eval()` 切换到评估模式。典型差异：

- Dropout：训练时随机丢弃激活，评估时关闭随机丢弃；
- BatchNorm：训练时使用当前 batch 统计并更新 running mean/variance，评估时使用保存的 running statistics。

checkpoint 推理通常是：

```python
model.load_state_dict(checkpoint["model"])
model.eval()
with torch.inference_mode():
    predictions = model(images)
```

`torch.no_grad()` 只关闭梯度图，不会关闭 Dropout，也不会阻止 BatchNorm 以训练模式更新统计量。因此验证必须同时写 `model.eval()` 和 `no_grad()`/`inference_mode()`。

### B6. 分类模型输出与损失

`C` 类单标签分类中，模型输出 logits：

```text
logits.shape = (batch_size, C)
target.shape = (batch_size,)
target.dtype = torch.long
target[i] in {0, 1, ..., C-1}
```

`CrossEntropyLoss` 内部等价于对 logits 做 `log_softmax` 再计算负对数似然。因此训练时通常直接：

```python
loss = nn.CrossEntropyLoss()(logits, labels)
```

不需要手动 `softmax`。先 softmax 再传入会改变数值形式，可能造成额外下溢、梯度变差，且不是该 loss 的预期输入。只有在展示概率或做后处理时才使用：

```python
probabilities = logits.softmax(dim=1)
```

### B7. 参数初始化

- 零初始化：输出层的 bias 或某些特殊参数可以使用；所有隐藏层权重都为零会让同层神经元得到相同梯度，无法打破对称性。
- Xavier/Glorot：根据输入和输出维度控制方差，常用于 `tanh`、线性层等。
- He/Kaiming：针对 ReLU 类激活，补偿正值截断带来的方差变化。

若同一隐藏层所有权重都初始化为零，那么每个神经元看到相同输入、输出相同值、收到相同梯度，更新后仍然相同，网络不能学出有区分度的隐藏表示。随机初始化的主要作用之一就是打破这种对称性。

## C. 训练与验证闭环

### C1. 一个 batch 的完整顺序

```python
model.train()
for inputs, labels in data_loader:
    inputs = inputs.to(device, non_blocking=True)
    labels = labels.to(device, non_blocking=True)

    optimizer.zero_grad(set_to_none=True)
    logits = model(inputs)
    loss = loss_fn(logits, labels)
    loss.backward()
    optimizer.step()
```

每一步的作用：

1. 读取 batch：得到当前训练样本。
2. 移动到 device：保证输入和模型参数在同一设备。
3. 清零梯度：避免梯度跨 batch 累积。
4. 前向：计算预测 logits。
5. loss：把预测和标签变成可优化的标量。
6. 反向：根据链式法则计算参数梯度。
7. 更新：optimizer 根据梯度修改参数。
8. 记录：保存 loss、正确数、样本数等统计。

如果先 `optimizer.step()` 再 `loss.backward()`，step 使用的是旧梯度、零梯度或上一个 batch 遗留的梯度，当前 batch 的梯度要到下一步才可能生效，训练顺序错误。输入在 GPU 而模型在 CPU，前向时会产生 device mismatch。

### C2. epoch loss 的统计

若每个 batch 的 `loss` 是 batch 内均值，整个 epoch 的样本平均 loss 应为：

```python
total_loss += float(loss.item()) * batch_size
total_samples += batch_size
epoch_loss = total_loss / total_samples
```

不能简单写成：

```python
sum(batch_losses) / len(batch_losses)
```

因为最后一个 batch 可能更小，无权平均会让小 batch 和大 batch 的影响相同。样本加权才等价于所有样本 loss 的平均。

### C3. SGD 与 Adam

设梯度为 `g_t = grad_theta L(theta_t)`：

普通 SGD：

```text
theta_{t+1} = theta_t - eta * g_t
```

带 momentum 的 SGD：

```text
v_t = mu * v_{t-1} + g_t
theta_{t+1} = theta_t - eta * v_t
```

Adam：

```text
m_t = beta1 * m_{t-1} + (1-beta1) * g_t
v_t = beta2 * v_{t-1} + (1-beta2) * g_t^2
m_hat_t = m_t / (1-beta1^t)
v_hat_t = v_t / (1-beta2^t)
theta_{t+1} = theta_t - eta * m_hat_t / (sqrt(v_hat_t) + epsilon)
```

SGD 通常对学习率较敏感，但简单、更新噪声有时有利于泛化。Momentum 可以平滑方向并加速穿过一致的梯度方向。Adam 会按参数自适应缩放更新，对不同参数尺度和稀疏梯度较方便，但仍需要调学习率、weight decay 等。

Adam 训练 loss 更低只说明在当前训练目标上拟合得更好，不代表测试分布上的泛化一定更好。优化器会影响隐式正则、参数解、训练速度和过拟合程度，最终要看独立 validation/test 和多个 seed。

### C4. 学习率与 scheduler

- 固定学习率：每一步使用同一个 `eta`，简单但可能在后期震荡或收敛慢。
- 阶梯衰减：在指定 epoch 将学习率乘以因子，先快速学习，后期细化。
- 余弦退火：学习率按余弦曲线平滑降低。
- warmup：训练开始先从小学习率逐渐升高，避免大模型、大 batch 或 Adam 初始阶段更新过猛。

曲线诊断：

- train/val loss 都震荡或发散：学习率可能太大，先降低并检查梯度。
- loss 下降极慢且梯度正常：学习率可能太小，或模型/数据存在其他问题。
- 前期下降、scheduler 很早衰减后几乎不动：衰减过早或最低学习率太低。
- train loss 下降、val loss 上升：主要是过拟合，不能只靠继续降低学习率解释。

断点续训至少保存：

```python
optimizer.state_dict()
scheduler.state_dict()
current_epoch
global_step
```

否则恢复后学习率、momentum/Adam 的一阶二阶矩和 scheduler 位置都可能跳变。

### C5. 验证循环

```python
@torch.inference_mode()
def evaluate(model, data_loader, loss_fn, device):
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for inputs, labels in data_loader:
        inputs = inputs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        logits = model(inputs)
        loss = loss_fn(logits, labels)

        batch_size = labels.shape[0]
        total_loss += float(loss.item()) * batch_size
        total_correct += int((logits.argmax(dim=1) == labels).sum().item())
        total_samples += batch_size

    if total_samples == 0:
        raise ValueError("validation loader is empty")
    return {
        "loss": total_loss / total_samples,
        "accuracy": total_correct / total_samples,
    }
```

`model.eval()` 防止 Dropout 和 BatchNorm 以训练方式工作，`inference_mode()` 防止构建梯度图并降低开销。遍历整个验证集是为了得到总体样本的平均 loss 和 accuracy；只看一个 batch 方差很大，且可能碰巧偏向某些类别。

### C6. 混合精度与梯度裁剪

`autocast` 让适合的算子使用较低精度，从而减少显存和提高吞吐；`GradScaler` 先把 loss 放大，避免半精度反向时小梯度下溢，更新前再 unscale。

普通 AMP 训练顺序：

```python
scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

optimizer.zero_grad(set_to_none=True)
with torch.autocast(
    device_type=device.type,
    dtype=torch.float16,
    enabled=use_amp,
):
    logits = model(inputs)
    loss = loss_fn(logits, labels)

scaler.scale(loss).backward()
scaler.unscale_(optimizer)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
scaler.step(optimizer)
scaler.update()
```

如果不使用 AMP，直接 `loss.backward()`、裁剪、`optimizer.step()`。梯度裁剪应在 backward 之后、step 之前；使用 GradScaler 时必须先 `unscale_(optimizer)`，否则裁剪的是被放大的梯度。

需要裁剪的典型情况是 RNN/长序列、深层网络或训练中出现梯度爆炸。裁剪不能修复标签错误、模型输出错误或长期过大的学习率，只是限制异常更新。

### C7. 训练曲线诊断

1. **训练和验证 loss 都不下降**：先查标签、输入范围、输出 shape、参数是否注册、学习率、loss 是否真的参与 backward；再做极小数据过拟合。
2. **训练 loss 降、验证 loss 先降后升**：典型过拟合。检查 best epoch，尝试 early stopping、增强、weight decay、Dropout、减小模型。
3. **训练 loss 震荡并出现 NaN**：学习率过大、梯度爆炸、输入/标签中有 NaN/inf、AMP 溢出。记录梯度范数并检查 batch。
4. **训练准确率接近随机猜测**：模型没有学到有效信息，重点检查标签编码、输出类别数、损失输入、参数更新和学习率。
5. **训练准确率很高而验证接近随机**：强过拟合、训练/验证预处理不一致、划分分布变化或数据泄漏/标签错位。
6. **loss 下降但准确率不变**：logits 可能在同一分类边界内变得更自信；也可能 accuracy 统计错误、标签 dtype/编码错误，或类别极不平衡。检查 confusion matrix 和逐样本预测。

## D. 配置、日志与 checkpoint

### D1. 实验配置

配置至少应包含：

```text
data_dir, train/val split, normalization, augmentation
model name, input shape, num_classes, hidden/channel widths
optimizer name, learning_rate, weight_decay, momentum/betas
scheduler name, scheduler arguments
batch_size, epochs, gradient clipping, use_amp
seed, device, num_workers, pin_memory
output_dir, latest/best checkpoint path, log path
code version, package versions
```

把超参数集中在 dataclass、YAML 或 JSON 中，可以让一次实验有完整快照，避免同一个变量在多个函数中被悄悄覆盖，也方便恢复、比较和复现。

### D2. 日志指标

step 级至少记录：

- 当前 epoch、global step；
- batch loss、学习率；
- 可选的梯度范数、参数范数、吞吐、GPU 显存。

epoch 级至少记录：

- train loss、train accuracy；
- validation loss、validation accuracy；
- 当前学习率、最佳 epoch、耗时；
- checkpoint 路径和是否更新 best。

系统和复现信息包括：

- device、PyTorch/Python/NumPy 版本；
- GPU 型号、随机种子、git commit；
- 数据集版本、划分索引、配置文件；
- worker 数和 AMP 设置。

只保存最后一个 accuracy 无法判断过拟合发生在哪个 epoch、学习率是否导致震荡、是否存在不同 seed 的不稳定，也不能复盘训练过程。

### D3. `state_dict` 与 checkpoint

建议保存如下字典：

```python
{
    "checkpoint_version": 1,
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "scheduler": scheduler.state_dict() if scheduler else None,
    "epoch": epoch,
    "global_step": global_step,
    "best_metric": best_metric,
    "config": asdict(config) if is_dataclass(config) else dict(config),
    "rng_state": ...,
    "versions": ...,
}
```

只保存 `model.state_dict()` 只能恢复参数，不能恢复 optimizer 的 momentum/Adam moments、scheduler 位置、epoch/global step、最佳指标和随机增强状态。因此恢复后学习率、更新方向和数据顺序可能跳变，训练轨迹不会一致。

### D4. 保存 best 与 latest

- `latest.pt`：每个 epoch 结束后覆盖，表示最近一次完整状态。
- `best.pt`：当 validation metric 改善时覆盖，表示当前最优模型。
- 训练结束可另存 `final.pt`，不要把它和 best 混为一谈。

如果允许更细粒度恢复，可每隔固定 step 或在 epoch 内处理完一个安全边界后保存临时 checkpoint，并使用原子写入：先写临时文件，再替换正式文件。恢复时：

- 继续训练：加载 model、optimizer、scheduler、epoch 和随机状态；
- 只推理：只加载 model，调用 `eval()`；
- 最终测试：加载 `best.pt`，在 test 集上只评估一次。

### D5. 断点续训一致性

要让“连续运行 N 个 epoch”和“运行到 K 后恢复到 N”尽量一致，需要保持：

- 相同的初始模型参数；
- 相同 optimizer 和 scheduler 状态；
- 相同 epoch/global step；
- 相同数据划分、shuffle 生成器和 worker 随机状态；
- 相同 Python、NumPy、PyTorch CPU/CUDA RNG；
- 相同 AMP scaler 状态；
- 相同代码、依赖、硬件和确定性设置。

多 worker 会让样本预取、worker 随机增强和队列时序更复杂；CUDA 某些 kernel 非确定；不同版本或不同硬件的浮点归约顺序也会改变最后几位。因此工程上应比较 loss/accuracy 曲线和参数差异是否在容忍范围内，而不是默认要求 bitwise 一致。

### D6. 随机种子与确定性

```python
import os
import random

import numpy as np
import torch


def seed_everything(seed):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # 更强的可复现设置，代价是速度可能下降。
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    # 需要严格检查时再打开：
    # torch.use_deterministic_algorithms(True)


def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


generator = torch.Generator()
generator.manual_seed(seed)
loader = torch.utils.data.DataLoader(
    dataset,
    shuffle=True,
    worker_init_fn=seed_worker,
    generator=generator,
)
```

固定 seed 仍不能自动保证所有硬件、CUDA/cuDNN 版本和算子都 bitwise 一致。应报告 seed、均值和标准差，必要时启用确定性算法，并记录环境版本。

## E. PyTorch 代码训练题

### E1. 可复现的 batch 统计

下面的实现会验证 batch 结构、输入 shape、标签 dtype 和标签维度；统计量按所有输入元素计算，而不是对 batch 均值做无权平均。

```python
from collections import Counter

import torch


def inspect_loader(data_loader):
    batch_count = 0
    sample_count = 0
    value_count = 0
    label_counts = Counter()
    first_input_shape = None
    expected_sample_shape = None
    total = 0.0
    total_squared = 0.0
    minimum = None
    maximum = None

    for batch in data_loader:
        if not isinstance(batch, (tuple, list)) or len(batch) != 2:
            raise TypeError("each batch must be (inputs, labels)")
        inputs, labels = batch
        if not isinstance(inputs, torch.Tensor):
            raise TypeError("inputs must be a Tensor")
        if not isinstance(labels, torch.Tensor):
            raise TypeError("labels must be a Tensor")
        if inputs.ndim < 1:
            raise ValueError("inputs need a batch dimension")
        if labels.ndim != 1:
            raise ValueError("labels must have shape (B,)")
        if labels.dtype not in (
            torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8
        ):
            raise TypeError("labels must have an integer dtype")
        if inputs.shape[0] != labels.shape[0]:
            raise ValueError("input and label batch sizes differ")

        current_sample_shape = tuple(int(v) for v in inputs.shape[1:])
        if first_input_shape is None:
            first_input_shape = [int(v) for v in inputs.shape]
            expected_sample_shape = current_sample_shape
        elif current_sample_shape != expected_sample_shape:
            raise ValueError("input sample shape is inconsistent")

        values = inputs.detach().to(torch.float64)
        current_min = float(values.min().item()) if values.numel() else None
        current_max = float(values.max().item()) if values.numel() else None
        if current_min is not None:
            minimum = current_min if minimum is None else min(minimum, current_min)
            maximum = current_max if maximum is None else max(maximum, current_max)

        total += float(values.sum().item())
        total_squared += float((values * values).sum().item())
        value_count += int(values.numel())
        batch_count += 1
        current_size = int(labels.shape[0])
        sample_count += current_size
        label_counts.update(int(v) for v in labels.cpu().tolist())

    if batch_count == 0:
        raise ValueError("data_loader is empty")
    if value_count == 0:
        raise ValueError("inputs contain no values")

    mean_value = total / value_count
    variance = max(0.0, total_squared / value_count - mean_value**2)
    return {
        "batch_count": int(batch_count),
        "sample_count": int(sample_count),
        "first_input_shape": first_input_shape,
        "input_dtype": str(inputs.dtype),
        "input_min": float(minimum),
        "input_max": float(maximum),
        "input_mean": float(mean_value),
        "input_std": float(variance**0.5),
        "label_distribution": {
            str(label): int(count)
            for label, count in sorted(label_counts.items())
        },
    }
```

固定 toy dataset 测试：

```python
from torch.utils.data import DataLoader, TensorDataset

torch.manual_seed(0)
toy_x = torch.arange(24, dtype=torch.float32).reshape(6, 1, 2, 2)
toy_y = torch.tensor([0, 1, 0, 2, 1, 1], dtype=torch.long)
toy_loader = DataLoader(
    TensorDataset(toy_x, toy_y),
    batch_size=4,
    shuffle=False,
)
print(inspect_loader(toy_loader))

empty_loader = DataLoader(
    TensorDataset(torch.empty(0, 1), torch.empty(0, dtype=torch.long)),
    batch_size=2,
)
try:
    inspect_loader(empty_loader)
except ValueError as error:
    print("empty test passed:", error)

bad_labels = DataLoader(
    TensorDataset(torch.randn(2, 1), torch.tensor([0.0, 1.0])),
    batch_size=2,
)
try:
    inspect_loader(bad_labels)
except TypeError as error:
    print("dtype test passed:", error)
```

### E2. MLP 模型与参数检查

```python
import torch
from torch import nn


class SmallMLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes, dropout=0.0):
        super().__init__()
        for name, value in {
            "input_dim": input_dim,
            "hidden_dim": hidden_dim,
            "num_classes": num_classes,
        }.items():
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not 0.0 <= dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")

        self.flatten = nn.Flatten(start_dim=1)
        self.classifier = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, images):
        if images.ndim != 4:
            raise ValueError(
                "images must have shape (batch, channels, height, width)"
            )
        flattened = self.flatten(images)
        expected_dim = self.classifier[0].in_features
        if flattened.shape[1] != expected_dim:
            raise ValueError(
                f"flattened input has {flattened.shape[1]} features, "
                f"expected {expected_dim}"
            )
        return self.classifier(flattened)


def count_trainable_parameters(model):
    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )


model = SmallMLP(
    input_dim=3 * 32 * 32,
    hidden_dim=128,
    num_classes=10,
    dropout=0.2,
)
print("total:", count_trainable_parameters(model))
for name, module in model.named_modules():
    if name:
        parameter_count = sum(p.numel() for p in module.parameters())
        print(name, module.__class__.__name__, parameter_count)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
images = torch.randn(5, 3, 32, 32, device=device)
logits = model(images)
assert logits.shape == (5, 10)
assert logits.dtype == images.dtype
loss = logits.square().mean()
loss.backward()
assert any(
    parameter.grad is not None
    for parameter in model.parameters()
    if parameter.requires_grad
)
```

这里的 `Flatten(start_dim=1)` 保留 batch 维；层放在 `nn.Sequential` 中，所以参数会被注册。

### E3. 单 epoch 训练与评估

```python
import torch


def _check_classification_batch(inputs, labels):
    if not isinstance(inputs, torch.Tensor) or inputs.ndim < 2:
        raise ValueError("inputs must be a Tensor with a batch dimension")
    if not isinstance(labels, torch.Tensor) or labels.ndim != 1:
        raise ValueError("labels must have shape (B,)")
    if labels.dtype != torch.long:
        raise TypeError("labels must use torch.long")
    if inputs.shape[0] != labels.shape[0]:
        raise ValueError("input and label batch sizes differ")


def _check_logits(logits, labels):
    if not isinstance(logits, torch.Tensor) or logits.ndim != 2:
        raise ValueError("model output must have shape (B, C)")
    if logits.shape[0] != labels.shape[0]:
        raise ValueError("logit and label batch sizes differ")
    if labels.numel() and (
        int(labels.min()) < 0 or int(labels.max()) >= logits.shape[1]
    ):
        raise ValueError("label is outside the model class range")


def train_one_epoch(model, data_loader, loss_fn, optimizer, device):
    model.train()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for inputs, labels in data_loader:
        _check_classification_batch(inputs, labels)
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        _check_logits(logits, labels)
        loss = loss_fn(logits, labels)
        if loss.ndim != 0:
            raise ValueError("loss_fn must return a scalar loss")
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite training loss")

        loss.backward()
        optimizer.step()

        batch_size = int(labels.shape[0])
        total_loss += float(loss.detach().item()) * batch_size
        total_correct += int((logits.argmax(1) == labels).sum().item())
        total_samples += batch_size

    if total_samples == 0:
        raise ValueError("training loader is empty")
    return {
        "loss": total_loss / total_samples,
        "accuracy": total_correct / total_samples,
    }


@torch.no_grad()
def evaluate(model, data_loader, loss_fn, device):
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for inputs, labels in data_loader:
        _check_classification_batch(inputs, labels)
        inputs = inputs.to(device)
        labels = labels.to(device)
        logits = model(inputs)
        _check_logits(logits, labels)
        loss = loss_fn(logits, labels)
        if loss.ndim != 0:
            raise ValueError("loss_fn must return a scalar loss")

        batch_size = int(labels.shape[0])
        total_loss += float(loss.item()) * batch_size
        total_correct += int((logits.argmax(1) == labels).sum().item())
        total_samples += batch_size

    if total_samples == 0:
        raise ValueError("evaluation loader is empty")
    return {
        "loss": total_loss / total_samples,
        "accuracy": total_correct / total_samples,
    }
```

一个手工可检查的 toy 测试：

```python
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

torch.manual_seed(0)
toy_x = torch.tensor(
    [[2.0, 0.0], [0.0, 2.0], [-2.0, 0.0], [0.0, -2.0]]
)
toy_y = torch.tensor([0, 1, 1, 0], dtype=torch.long)
loader = DataLoader(TensorDataset(toy_x, toy_y), batch_size=2, shuffle=False)

toy_model = nn.Linear(2, 2)
toy_loss = nn.CrossEntropyLoss()
toy_optimizer = torch.optim.SGD(toy_model.parameters(), lr=0.1)
before = [p.detach().clone() for p in toy_model.parameters()]
train_result = train_one_epoch(
    toy_model, loader, toy_loss, toy_optimizer, torch.device("cpu")
)
after = list(toy_model.parameters())
assert any(not torch.equal(a, b) for a, b in zip(before, after))

saved_parameters = [p.detach().clone() for p in toy_model.parameters()]
saved_grads = [
    None if p.grad is None else p.grad.detach().clone()
    for p in toy_model.parameters()
]
eval_result = evaluate(
    toy_model, loader, toy_loss, torch.device("cpu")
)
assert all(
    torch.equal(a, b)
    for a, b in zip(saved_parameters, toy_model.parameters())
)
assert all(
    (a is None and b is None) or torch.equal(a, b)
    for a, b in zip(saved_grads, [p.grad for p in toy_model.parameters()])
)
print(train_result, eval_result)
```

### E4. 配置驱动的 CIFAR-10 训练脚本

下面是一个可运行的最小 CNN 训练入口。实际实验时可把模型替换成 torchvision 的 ResNet，并把 `num_workers`、batch size 和 epoch 数按机器资源调整。

```python
from dataclasses import asdict, dataclass
import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms


@dataclass
class TrainConfig:
    data_dir: str = "./data"
    output_dir: str = "./runs/week5"
    seed: int = 0
    batch_size: int = 128
    epochs: int = 10
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    num_workers: int = 2
    use_amp: bool = False


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


class TinyCifarCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def _worker_init_fn(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def run_experiment(config: TrainConfig):
    seed_everything(config.seed)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    mean = (0.4914, 0.4822, 0.4465)
    std = (0.2470, 0.2435, 0.2616)
    train_transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    val_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])

    # 两个 dataset 使用相同的底层样本和固定索引，但 transform 分开。
    train_base = datasets.CIFAR10(
        config.data_dir, train=True, download=True,
        transform=train_transform,
    )
    val_base = datasets.CIFAR10(
        config.data_dir, train=True, download=False,
        transform=val_transform,
    )
    split_generator = torch.Generator().manual_seed(config.seed)
    indices = torch.randperm(len(train_base), generator=split_generator).tolist()
    val_size = 5000
    val_indices = indices[:val_size]
    train_indices = indices[val_size:]
    train_set = Subset(train_base, train_indices)
    val_set = Subset(val_base, val_indices)

    loader_generator = torch.Generator().manual_seed(config.seed + 1)
    train_loader = DataLoader(
        train_set,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=config.num_workers > 0,
        worker_init_fn=_worker_init_fn,
        generator=loader_generator,
    )
    val_loader = DataLoader(
        val_set,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=device.type == "cuda",
        persistent_workers=config.num_workers > 0,
        worker_init_fn=_worker_init_fn,
    )

    model = TinyCifarCNN().to(device)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config.epochs
    )
    amp_enabled = config.use_amp and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)
    history = []
    best_accuracy = -float("inf")

    for epoch in range(config.epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_samples = 0
        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(
                device_type=device.type,
                dtype=torch.float16,
                enabled=amp_enabled,
            ):
                logits = model(images)
                loss = loss_fn(logits, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            count = int(labels.shape[0])
            train_loss += float(loss.detach().item()) * count
            train_correct += int((logits.argmax(1) == labels).sum().item())
            train_samples += count

        train_metrics = {
            "loss": train_loss / train_samples,
            "accuracy": train_correct / train_samples,
        }
        val_metrics = evaluate(model, val_loader, loss_fn, device)
        scheduler.step()
        record = {
            "epoch": epoch + 1,
            "train_loss": train_metrics["loss"],
            "train_accuracy": train_metrics["accuracy"],
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "learning_rate": optimizer.param_groups[0]["lr"],
        }
        history.append(record)
        print(record)

        checkpoint = {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict(),
            "epoch": epoch + 1,
            "history": history,
            "config": asdict(config),
            "device": str(device),
        }
        torch.save(checkpoint, output_dir / "latest.pt")
        if val_metrics["accuracy"] > best_accuracy:
            best_accuracy = val_metrics["accuracy"]
            torch.save(checkpoint, output_dir / "best.pt")

    (output_dir / "config.json").write_text(
        json.dumps({
            "config": asdict(config),
            "device": str(device),
            "torch_version": torch.__version__,
            "numpy_version": np.__version__,
            "python_version": __import__("sys").version,
        }, indent=2),
        encoding="utf-8",
    )
    (output_dir / "history.json").write_text(
        json.dumps(history, indent=2), encoding="utf-8"
    )

    epochs = [item["epoch"] for item in history]
    plt.figure()
    plt.plot(epochs, [item["train_loss"] for item in history], label="train")
    plt.plot(epochs, [item["val_loss"] for item in history], label="val")
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "loss.png")
    plt.close()

    return history
```

上面的入口依赖 E3 的 `evaluate`，也可以直接复用。较新的 PyTorch 推荐 `torch.amp.GradScaler("cuda", ...)`；如果本地版本较旧，应根据版本改成 `torch.cuda.amp.GradScaler(...)`。

多组实验应使用不同的输出目录，不要覆盖结果：

```python
from dataclasses import replace
import numpy as np

base = TrainConfig(epochs=10)
all_results = []
for learning_rate in [3e-4, 1e-3, 3e-3]:
    for seed in [0, 1, 2]:
        config = replace(
            base,
            seed=seed,
            learning_rate=learning_rate,
            output_dir=f"./runs/week5/lr-{learning_rate:g}-seed-{seed}",
        )
        history = run_experiment(config)
        best = max(item["val_accuracy"] for item in history)
        all_results.append({
            "learning_rate": learning_rate,
            "seed": seed,
            "best_val_accuracy": best,
        })

for learning_rate in [3e-4, 1e-3, 3e-3]:
    values = [
        row["best_val_accuracy"]
        for row in all_results
        if row["learning_rate"] == learning_rate
    ]
    print(
        learning_rate,
        "mean=", float(np.mean(values)),
        "std=", float(np.std(values, ddof=1)),
    )
```

报告时不能只写“最好一次跑到多少”，应报告每个设置的均值、标准差、best epoch、训练时间和失败样本/类别分析。

### E5. 断点续训实验

```python
from dataclasses import asdict, is_dataclass
import json
import random
from pathlib import Path

import numpy as np
import torch


CHECKPOINT_VERSION = 1


def _capture_rng_state():
    result = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch_cpu": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        result["torch_cuda"] = torch.cuda.get_rng_state_all()
    return result


def _restore_rng_state(state):
    if not state:
        return
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch_cpu"])
    if torch.cuda.is_available() and state.get("torch_cuda") is not None:
        torch.cuda.set_rng_state_all(state["torch_cuda"])


def save_checkpoint(
    path,
    model,
    optimizer,
    scheduler,
    epoch,
    global_step,
    best_metric,
    config,
):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(epoch, int) or epoch < 0:
        raise ValueError("epoch must be a non-negative integer")
    if not isinstance(global_step, int) or global_step < 0:
        raise ValueError("global_step must be a non-negative integer")

    payload = {
        "checkpoint_version": CHECKPOINT_VERSION,
        "model": model.state_dict(),
        "optimizer": None if optimizer is None else optimizer.state_dict(),
        "scheduler": None if scheduler is None else scheduler.state_dict(),
        "epoch": epoch,
        "global_step": global_step,
        "best_metric": best_metric,
        "config": (
            asdict(config)
            if is_dataclass(config)
            else dict(config)
            if isinstance(config, dict)
            else config
        ),
        "rng_state": _capture_rng_state(),
        "torch_version": torch.__version__,
    }
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary_path)
    temporary_path.replace(path)


def load_checkpoint(
    path,
    model,
    optimizer=None,
    scheduler=None,
    map_location="cpu",
):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"checkpoint does not exist: {path}")
    try:
        checkpoint = torch.load(
            path, map_location=map_location, weights_only=False
        )
    except Exception as error:
        raise RuntimeError(f"failed to read checkpoint: {path}") from error
    if not isinstance(checkpoint, dict):
        raise ValueError("checkpoint must be a dictionary")
    if checkpoint.get("checkpoint_version") != CHECKPOINT_VERSION:
        raise ValueError("unsupported or missing checkpoint version")
    if "model" not in checkpoint:
        raise ValueError("checkpoint is missing model state")

    try:
        model.load_state_dict(checkpoint["model"])
    except Exception as error:
        raise ValueError("model state does not match current model") from error

    if optimizer is not None:
        if checkpoint.get("optimizer") is None:
            raise ValueError("optimizer state is missing")
        optimizer.load_state_dict(checkpoint["optimizer"])
    if scheduler is not None:
        if checkpoint.get("scheduler") is None:
            raise ValueError("scheduler state is missing")
        scheduler.load_state_dict(checkpoint["scheduler"])

    required = ("epoch", "global_step", "best_metric", "config")
    missing = [key for key in required if key not in checkpoint]
    if missing:
        raise ValueError(f"checkpoint is missing fields: {missing}")
    _restore_rng_state(checkpoint.get("rng_state"))
    return {
        "epoch": int(checkpoint["epoch"]),
        "global_step": int(checkpoint["global_step"]),
        "best_metric": checkpoint["best_metric"],
        "config": checkpoint["config"],
        "torch_version": checkpoint.get("torch_version"),
    }
```

仅推理时：

```python
metadata = load_checkpoint(
    "best.pt",
    model=model,
    optimizer=None,
    scheduler=None,
    map_location=device,
)
model.eval()
```

续训时：

```python
metadata = load_checkpoint(
    "latest.pt",
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    map_location=device,
)
start_epoch = metadata["epoch"]
global_step = metadata["global_step"]
best_metric = metadata["best_metric"]

for epoch in range(start_epoch, config.epochs):
    ...
```

实验设计：

1. 固定 seed 和初始配置，连续训练 `N` 个 epoch，保存每个 epoch 的 history 和最终参数。
2. 另起一次同样的训练，只运行到 `K`，保存 checkpoint，再加载并运行到 `N`。
3. 比较每个 epoch 的 train/val loss、accuracy，比较最终参数的最大绝对差和验证指标。
4. 如果不完全一致，检查保存的 optimizer/scheduler/RNG、DataLoader generator、worker 随机性、AMP scaler、代码和硬件版本。

### E6. 过拟合诊断与最小数据集实验

实验目的不是追求一个漂亮数字，而是确认自己能从曲线和失败样本解释过拟合。

一个可执行的实验设置：

```python
from dataclasses import replace

base = TrainConfig(
    batch_size=32,
    epochs=50,
    learning_rate=1e-3,
    weight_decay=0.0,
    output_dir="./runs/week5/overfit/base",
)

settings = [
    ("base", base),
    ("augmentation", replace(base, output_dir="./runs/week5/overfit/aug")),
    (
        "weight_decay",
        replace(
            base,
            weight_decay=1e-3,
            output_dir="./runs/week5/overfit/weight-decay",
        ),
    ),
]

for name, config in settings:
    for seed in [0, 1, 2]:
        run_experiment(
            replace(
                config,
                seed=seed,
                output_dir=f"{config.output_dir}/seed-{seed}",
            )
        )
```

为了故意制造过拟合，可以只取固定的 256 或 512 张训练图，保留一个固定 validation 子集，使用容量较大的 CNN、较少正则化和较多 epoch。记录：

```text
epoch, train_loss, train_accuracy, val_loss, val_accuracy, learning_rate
```

最佳验证 epoch 的定义应明确，例如：

```python
best_epoch = min(history, key=lambda row: row["val_loss"])["epoch"]
```

报告至少包含：

- train loss 继续下降而 val loss 上升的拐点；
- 两种缓解方法在最佳 epoch 的验证指标；
- 每个方法多个 seed 的均值和标准差；
- 至少 20 个验证失败样本的图片、真实标签、预测标签和置信度；
- 失败是否集中于某些类别、背景、姿态或图像质量；
- 哪个结论在不同 seed 下稳定，哪个结论不稳定。

失败样本可这样收集：

```python
@torch.inference_mode()
def collect_mistakes(model, data_loader, device, limit=20):
    model.eval()
    mistakes = []
    for images, labels in data_loader:
        logits = model(images.to(device))
        probabilities = logits.softmax(dim=1)
        predictions = logits.argmax(dim=1).cpu()
        for index, (label, prediction) in enumerate(
            zip(labels, predictions)
        ):
            if int(label) != int(prediction):
                mistakes.append({
                    "image": images[index].cpu(),
                    "label": int(label),
                    "prediction": int(prediction),
                    "confidence": float(
                        probabilities[index, prediction].item()
                    ),
                })
                if len(mistakes) >= limit:
                    return mistakes
    return mistakes
```

训练集准确率高只能说明模型能记住训练样本，不能证明它对未见样本、分布变化或真实机器人观测有效。验证集曲线、独立测试集、失败类别和多 seed 才能支持泛化结论。

## F. 应用与常见误区

### F1. 从数据到机器人策略

一个图像到离散动作的 episode 可以设计为：

```text
episode_id
  ├─ observation[t]
  │    ├─ rgb: (H, W, 3), uint8 or float32
  │    ├─ proprioception: joint positions/velocities
  │    ├─ timestamp_ns
  │    └─ camera/frame metadata
  ├─ action[t]
  │    ├─ discrete_action: int in [0, num_actions)
  │    ├─ optional action_mask
  │    └─ timestamp_ns
  └─ episode metadata
       ├─ task/instruction
       ├─ robot id
       ├─ camera calibration version
       ├─ success/failure
       └─ dataset version
```

构造 batch 时要明确：

- observation 与 action 的时间对齐，例如 action at `t` 是否作用于 observation at `t`；
- 图像布局、dtype、像素范围和 mean/std；
- 关节位置、速度、力等连续量的归一化范围；
- 离散动作的编码表，不能只保存整数而不保存语义；
- 不同长度 episode 如何 padding、截断和使用 attention/action mask；
- 缺失帧、相机掉帧和时间戳乱序如何处理；
- train/validation/test 按 episode 或场景划分，不能把同一 episode 的相邻帧拆到不同集合。

schema 应保存单位、坐标系、时间基准、采样频率、动作延迟、相机内外参版本、归一化统计量和标签定义。机器人学习中，时间对齐错误往往比模型结构错误更难发现。

### F2. 训练结果解释

1. **train 92%，val 54%**：最可能是过拟合，也要排查 train/val 预处理不一致、数据划分偏移、标签错位和重复泄漏。先看两条 loss 曲线、每类 accuracy、confusion matrix 和 transform；修复实验可以比较加数据增强/weight decay/early stopping，并在固定 split 和多个 seed 上重跑。
2. **第 6 epoch 的 val loss 最低，之后升高**：第 6 epoch 可能是最佳 checkpoint，之后模型开始拟合训练集细节。检查 best 保存逻辑是否按 validation loss 正确更新；实验上使用第 6 epoch checkpoint 与最后 checkpoint 在 test 上比较。
3. **换 seed 后 val 从 54% 变 48%**：可能是小验证集、数据量少、随机增强强、优化不稳定或划分差异。检查 split 是否固定、报告多个 seed 均值/标准差；增加 seed 重复并固定划分，区分“初始化不稳定”和“划分不稳定”。
4. **恢复后第一轮 loss 突然变大**：可能没有恢复 optimizer/scheduler/RNG、学习率被重新初始化、恢复位置错了一轮、模型在 `train()` 下 BatchNorm 统计变化，或 DataLoader 顺序改变。检查 checkpoint 字段、恢复前后 `optimizer.param_groups[0]["lr"]`、global step、scheduler state 和首个 batch；与不中断对照逐 epoch 比较。

### F3. 常见错误判断

1. **错误**：`model.eval()` 会关闭梯度。  
   **修正**：`eval()` 只改变模块行为；关闭梯度要用 `no_grad()` 或 `inference_mode()`。
2. **错误**：`no_grad()` 会让 Dropout 自动切换验证行为。  
   **修正**：不会，必须显式 `model.eval()`。
3. **错误**：先 softmax 再传给 `CrossEntropyLoss` 更规范。  
   **修正**：直接传 logits；CrossEntropyLoss 内部已处理 log-softmax。
4. **错误**：只保存模型权重足以恢复训练。  
   **修正**：还需要 optimizer、scheduler、epoch/global step、配置和随机状态。
5. **错误**：batch size 加倍后学习率不需要重新考虑。  
   **修正**：有效梯度噪声和每 epoch 的 step 数都会改变，学习率和 scheduler 需要重新验证；线性缩放只是可测试的经验规则，不是定理。
6. **错误**：验证准确率提升就说明泛化良好。  
   **修正**：可能是验证集过拟合或方差偶然下降，需要独立 test、多 seed 和失败分析。
7. **错误**：固定一个 seed 后不需要报告方差。  
   **修正**：单个 seed 不能反映初始化、划分和增强带来的不确定性。
8. **错误**：checkpoint 能加载就说明恢复训练正确。  
   **修正**：还要检查 optimizer/scheduler/RNG、恢复 epoch、首个 batch、曲线和不中断对照。

### F4. 训练闭环排错清单

按从数据到 optimizer 的顺序：

1. 可视化原图、归一化后的图像和标签，确认标签与图像对应。
2. 打印输入 `shape/dtype/min/max/mean/std`，检查是否有 NaN/inf。
3. 确认标签从 `0` 开始、范围合法、dtype 为 `long`，类别数与输出一致。
4. 检查模型输出是 `(B, C)`，没有错误的 softmax、额外 batch 维或类别维。
5. 检查层是否注册在 `ModuleList`/`Sequential`/Module 属性中，参数数量是否非零。
6. 在 `loss.backward()` 后检查每层梯度是否存在、有限、不是全零。
7. 检查参数是否真的改变，打印学习率、参数范数和梯度范数。
8. 尝试更小和更大的学习率，检查 optimizer 是否绑定了 `model.parameters()`。
9. 确认训练时 `model.train()`，验证时 `model.eval()`；不要在训练前向外包 `no_grad()`。
10. 暂时关闭 AMP、复杂 scheduler 和数据增强，缩小问题范围。
11. 检查是否误加载了旧 checkpoint、加载后又覆盖了新参数，或恢复 epoch/off-by-one 错误。
12. 用 8 到 32 个样本反复训练，确认模型能否把极小训练集过拟合；如果做不到，优先查数据、loss、输出和 optimizer，而不是增加数据。

## G. 本周验收

参考自评可以这样填写，但最终应换成自己的实验结果：

1. 我能解释 Tensor、计算图、leaf tensor、`requires_grad` 和梯度累积，并能说明为什么每个 batch 要清零梯度。
2. 我能实现返回稳定 `(input, label)` 结构的 Dataset，并用 DataLoader 控制 batch、shuffle、worker 和 pin memory。
3. 我能独立写出包含 `train()`、前向、loss、backward、step、样本加权统计和 device 管理的训练 loop。
4. 我能区分 `train()`/`eval()` 与 `no_grad()`/`inference_mode()`：前者改变模块行为，后者改变 autograd 行为。
5. 我能保存并恢复 model、optimizer、scheduler、epoch、global step、配置和随机状态，并用不中断曲线做对照。
6. 我能通过 loss、accuracy、梯度范数和极小数据过拟合实验定位过拟合、学习率问题或标签错误。
7. 我完成了 CIFAR-10 实验，比较了至少三组学习率或两种 optimizer，并报告多个 seed 的均值和离散程度。
8. 我完成了 checkpoint 恢复实验，比较了两条曲线、最终参数差异和验证指标差异。
9. 还需要继续验证的地方应具体记录，例如：不同 PyTorch/CUDA 版本的 bitwise reproducibility、AMP 下的数值差异、DataLoader 多 worker 的随机增强顺序等。

本周的最低合格证据不是一张“最高 accuracy”截图，而是：可运行代码、完整配置、训练/验证曲线、best/latest checkpoint、多个 seed 的统计，以及至少 20 个失败样本或失败类别的解释。
