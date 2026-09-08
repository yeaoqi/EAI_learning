# 05 PyTorch 训练闭环自测

本文件用于第五周学习与自测。建议先独立作答；不确定的地方标记为“待补充”，完成代码实验后再回来修正答案。

本周目标：理解 PyTorch 的张量、自动求导、`Dataset`、`DataLoader`、`nn.Module`、损失函数、优化器和 checkpoint，能够独立完成一个可复现的 CIFAR-10 训练闭环，并根据曲线定位过拟合、优化不稳定和断点续训问题。

## A. Tensor 与 autograd

### A1. Tensor、dtype、device 与 shape

请解释 PyTorch `Tensor` 与 NumPy 数组的主要区别。`dtype`、`device`、`shape` 和 `stride` 分别描述什么？为什么同一个模型的输入、参数和标签通常需要满足特定的 dtype 和 device 约束？

答案：


### A2. 广播与批量维度

设：

```text
input_batch.shape = (batch_size, feature_dim)
weight.shape = (feature_dim, output_dim)
bias.shape = (output_dim,)
```

请推导 `output = input_batch @ weight + bias` 的结果形状，并解释 bias 是如何广播的。再举出一个广播成功但语义错误的例子。

答案：


### A3. 叶子张量与计算图

什么是 leaf tensor？`requires_grad=True` 的作用是什么？请区分以下对象的行为：

1. 用户直接创建且需要梯度的参数；
2. 对参数做运算得到的中间张量；
3. 在 `torch.no_grad()` 中得到的张量；
4. 调用 `detach()` 得到的张量。

答案：


### A4. 反向传播与链式法则

设：

```text
z = weight * input + bias
loss = (z - target)^2 / 2
```

请手算 `d loss / d weight`、`d loss / d input` 和 `d loss / d bias`，并说明 `loss.backward()` 如何沿计算图得到这些梯度。

答案：


### A5. 梯度累积

为什么 PyTorch 默认会累积 `.grad`，而不是每次 `backward()` 自动覆盖？请写出一个连续处理两个 batch 时的伪代码，并说明 `optimizer.zero_grad()` 应放在哪里。若忘记清零，会怎样影响参数更新？

答案：


### A6. `detach`、`no_grad` 与 `inference_mode`

比较 `tensor.detach()`、`with torch.no_grad()` 和 `with torch.inference_mode()` 的用途、计算图行为和常见使用场景。验证集评估和把模型输出转成 NumPy 数组时分别应如何使用？

答案：


### A7. 自动求导的边界

请解释以下情况为什么可能导致梯度为 `None`、梯度为零或运行时错误：

- 参数没有参与当前 loss；
- 对 tensor 调用了 `.item()` 后继续计算；
- 在计算图中原地修改需要梯度的 tensor；
- 在 `torch.no_grad()` 中完成了训练前向；
- 对非标量 loss 直接调用 `backward()`。

答案：


## B. Dataset、DataLoader 与 Module

### B1. `Dataset` 接口

`torch.utils.data.Dataset` 通常需要实现哪些方法？`__getitem__` 应该返回什么结构？请设计一个图像分类 dataset 的样本格式，并说明为什么应在 dataset 或 transform 阶段统一数据类型、范围和标签类型。

答案：


### B2. `DataLoader` 参数

解释以下参数对训练行为和性能的影响：

- `batch_size`
- `shuffle`
- `drop_last`
- `num_workers`
- `pin_memory`
- `persistent_workers`

哪些参数只影响吞吐，哪些参数可能改变训练数据顺序或统计结果？在验证集上是否应该使用 `shuffle=True`？

答案：


### B3. 数据划分与泄漏

请设计训练集、验证集和测试集的划分流程。为什么不能根据测试集表现选择 epoch 数、学习率或数据增强？列出至少三种 CIFAR-10 训练中可能发生的数据泄漏。

答案：


### B4. `nn.Module` 与参数注册

解释 `nn.Module`、`nn.Parameter`、`ModuleList`、`Sequential` 和普通 Python list 的区别。为什么把若干层放在普通 list 中，可能导致 `model.parameters()` 找不到这些层的参数？

答案：


### B5. `train()` 与 `eval()`

`model.train()` 和 `model.eval()` 分别改变哪些模块的行为？以 Dropout 和 BatchNorm 为例说明训练模式、验证模式和 checkpoint 推理模式的区别。为什么只使用 `torch.no_grad()` 还不够？

答案：


### B6. 分类模型输出与损失

对于 `C` 类单标签分类任务，模型最后一层通常输出什么？`CrossEntropyLoss` 的输入和 target 形状、dtype 分别是什么？为什么训练时通常不需要在 logits 前手动调用 softmax？

答案：


### B7. 参数初始化

比较零初始化、Xavier 初始化和 He 初始化的适用场景。为什么把所有线性层权重初始化为零，可能导致隐藏层学不到有区分度的表示？

答案：


## C. 训练与验证闭环

### C1. 一个 batch 的完整顺序

请写出训练一个 batch 的正确操作顺序，并解释每一步的目的：

```text
读取 batch
移动到 device
清零梯度
前向计算
计算 loss
反向传播
更新参数
记录指标
```

如果把 `optimizer.step()` 放在 `loss.backward()` 之前会发生什么？如果把数据移到 GPU 但模型仍在 CPU 上会发生什么？

答案：


### C2. epoch loss 的统计

设每个 batch 的 loss 是 batch 内样本的平均值，但最后一个 batch 的大小可能更小。如何计算整个 epoch 的样本平均 loss？为什么不能简单地对 batch loss 做无权平均？

答案：


### C3. SGD 与 Adam

写出 SGD、带 momentum 的 SGD 和 Adam 的参数更新核心公式。比较它们对学习率、梯度噪声、参数尺度和泛化的敏感性。为什么“Adam 训练 loss 更低”不等于“Adam 的测试准确率一定更高”？

答案：


### C4. 学习率与 scheduler

解释固定学习率、阶梯衰减、余弦退火和 warmup 的基本思想。如何从训练/验证曲线判断学习率过大、过小或衰减过早？使用 scheduler 时应记录哪些状态，才能正确恢复训练？

答案：


### C5. 验证循环

请设计一个验证函数，要求：

- 切换到 `eval()`；
- 禁止构建梯度图；
- 累计平均 loss 和准确率；
- 不修改模型参数和 BatchNorm 统计量；
- 返回可序列化的标量结果。

为什么验证阶段仍然需要遍历整个验证集，而不能只看一个 batch？

答案：


### C6. 混合精度与梯度裁剪

解释自动混合精度中的 autocast 和 GradScaler 分别解决什么问题。什么情况下需要梯度裁剪？请说明梯度裁剪应放在 `backward()` 和 `optimizer.step()` 的哪个位置，以及使用 GradScaler 时有什么额外步骤。

答案：


### C7. 训练曲线诊断

分别说明以下曲线现象最可能暗示的问题，并列出验证步骤：

1. 训练 loss 和验证 loss 都几乎不下降；
2. 训练 loss 下降，验证 loss 先降后升；
3. 训练 loss 剧烈震荡并出现 `NaN`；
4. 训练准确率接近随机猜测；
5. 训练准确率很高但验证准确率接近随机猜测；
6. loss 看似下降，但准确率完全不变。

答案：


## D. 配置、日志与 checkpoint

### D1. 实验配置

请列出一个 CIFAR-10 实验配置中至少应显式记录的字段，覆盖：

- 数据与增强；
- 模型结构；
- 优化器和 scheduler；
- batch size、epoch 数和学习率；
- 随机种子和 device；
- checkpoint 与日志路径。

为什么不应把关键超参数散落在训练脚本的多个函数里？

答案：


### D2. 日志指标

训练过程中至少应记录哪些 step 级和 epoch 级指标？请区分训练集指标、验证集指标、系统性能指标和可复现性信息。为什么只记录最后一个 accuracy 不足以支持实验分析？

答案：


### D3. `state_dict` 与 checkpoint

解释以下对象各自应如何保存：

- 模型参数；
- 优化器状态；
- scheduler 状态；
- 当前 epoch 和 global step；
- 最佳验证指标；
- 随机数生成器状态；
- 实验配置和代码版本。

为什么只保存 `model.state_dict()` 不能保证断点续训后轨迹一致？

答案：


### D4. 保存 best 与 latest

请设计 `latest.pt` 和 `best.pt` 的保存策略。什么时候覆盖它们？如果训练在 epoch 中途被终止，怎样减少丢失进度？恢复后如何判断是继续训练、只做评估，还是加载最佳模型进行测试？

答案：


### D5. 断点续训一致性

假设训练先连续运行 `N` 个 epoch，再从第 `K` 个 epoch 的 checkpoint 恢复运行到 `N`；另一种方式是从头运行 `N` 个 epoch。理论上哪些状态需要一致，才能让两次结果尽量一致？为什么多 worker 数据加载、CUDA 非确定性和随机增强会使“完全一致”变得困难？

答案：


### D6. 随机种子与确定性

请列出需要设置随机种子的随机源，至少覆盖 Python、NumPy、PyTorch CPU、PyTorch CUDA 和 DataLoader worker。解释“固定随机种子”不能自动保证所有硬件和版本上的 bitwise 一致。

答案：


## E. PyTorch 代码训练题

### E1. 可复现的 batch 统计

补全函数，读取一个 `DataLoader`，统计标签分布和输入张量的形状、dtype、最小值、最大值、均值与标准差。

```python
from collections import Counter

import torch


def inspect_loader(data_loader):
    """返回可 JSON 序列化的 batch 与数据统计信息。"""
    pass
```

要求：

- 检查 `data_loader` 至少能产生一个 batch；
- 支持标签为一维整数 tensor；
- 记录 batch 数、样本数、首个 batch 的输入形状；
- 对输入数据计算全局样本级统计，而不是只返回最后一个 batch；
- 返回值只能包含 Python 标量、字符串、列表和字典；
- 至少构造一个固定随机种子的 toy dataset 做测试；
- 测试空 dataset、标签 dtype 错误和输入 shape 不一致的情况。

答案：


### E2. MLP 模型与参数检查

补全一个用于图像分类的 MLP 和参数统计函数。

```python
import torch
from torch import nn


class SmallMLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes, dropout=0.0):
        super().__init__()
        pass

    def forward(self, images):
        pass


def count_trainable_parameters(model):
    pass
```

要求：

- 输入支持 `(batch_size, channels, height, width)`；
- 在模型内部明确完成 flatten；
- 输出 shape 为 `(batch_size, num_classes)`；
- 拒绝非正维度和不在 `[0, 1)` 范围内的 dropout；
- 使用 `nn.Module` 子模块，不能把层只放在普通 list 中；
- 用随机输入做 shape、dtype、device 和反向传播测试；
- 报告每个子模块的参数量和总可训练参数量。

答案：


### E3. 单 epoch 训练与评估

补全下面两个函数，完成一个通用分类训练闭环。

```python
def train_one_epoch(model, data_loader, loss_fn, optimizer, device):
    pass


@torch.no_grad()
def evaluate(model, data_loader, loss_fn, device):
    pass
```

要求：

- 正确处理 `model.train()`、`model.eval()` 和 device；
- 训练函数执行清零梯度、前向、loss、反向和参数更新；
- 以样本数加权统计 epoch loss；
- 返回包含 `loss` 和 `accuracy` 的字典；
- 检查输入 batch、标签 dtype、类别范围和模型输出形状；
- 用一个可手工计算结果的 toy dataset 验证 loss 与 accuracy；
- 运行至少两个 batch，并确认参数确实发生变化；
- 验证阶段确认参数和梯度状态没有被意外修改。

答案：


### E4. 配置驱动的 CIFAR-10 训练脚本

实现一个配置驱动的训练入口：

```python
from dataclasses import dataclass


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


def run_experiment(config: TrainConfig):
    pass
```

要求：

- 使用 CIFAR-10 train/test 数据，并从训练集划出验证集；
- 训练和验证 transform 的随机性必须分开；
- 使用一个明确的 CNN 或 ResNet 风格模型；
- 保存每个 epoch 的训练/验证 loss、accuracy 和学习率；
- 保存 `latest.pt`、`best.pt` 和最终配置；
- 支持 CPU 运行，并在可用时支持 CUDA；
- 固定随机种子，记录 PyTorch、Python、NumPy 版本和 device；
- 实验结束后输出至少一张 loss/accuracy 曲线；
- 至少比较三个学习率或两个优化器设置，并报告多个随机种子的均值和离散程度；
- 不要只报告最好一次运行的结果。

答案：


### E5. 断点续训实验

补全 checkpoint 工具：

```python
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
    pass


def load_checkpoint(
    path,
    model,
    optimizer=None,
    scheduler=None,
    map_location="cpu",
):
    pass
```

要求：

- 保存和恢复模型、优化器、scheduler、epoch、global step、最佳指标和配置；
- 尽可能保存 Python、NumPy、PyTorch CPU/CUDA 的随机状态；
- 载入时检查 checkpoint 版本和关键配置；
- 支持仅加载模型进行推理；
- 对不存在的文件、损坏文件和结构不完整的文件给出清晰错误；
- 设计一个实验：先训练若干 epoch 保存，再恢复训练；同时做一条不中断的对照曲线；
- 比较两条曲线、最终参数差异和验证指标差异，并解释无法完全一致时的原因。

答案：


### E6. 过拟合诊断与最小数据集实验

设计一个可复现实验，故意让模型在很小的训练集上过拟合，然后比较至少两种缓解方法。

要求：

- 固定训练/验证划分和随机种子；
- 记录训练 loss、验证 loss、训练 accuracy 和验证 accuracy；
- 至少比较两种方法，例如数据增强、weight decay、Dropout、early stopping 或减少模型容量；
- 画出曲线并标注最佳验证 epoch；
- 给出至少 20 个验证失败样本或失败类别的分析；
- 说明“训练集准确率高”为什么不能单独证明模型可用；
- 报告不同随机种子下结论是否稳定。

答案：


## F. 应用与常见误区

### F1. 从数据到机器人策略

假设后续要训练一个从相机图像预测机器人离散动作的模型。请设计从 episode 数据到 batch 的数据流，明确 observation、action、时间戳、归一化、padding 或裁剪策略，并说明哪些信息需要写进数据 schema。

答案：


### F2. 训练结果解释

某模型训练结束后得到以下现象：

- 训练准确率 `92%`，验证准确率 `54%`；
- 验证 loss 在第 6 个 epoch 最低，之后继续升高；
- 换一个随机种子后验证准确率变为 `48%`；
- 恢复 checkpoint 后第一轮 loss 突然变大。

请分别提出最可能的解释、最先检查的日志或代码位置，以及一个可验证的修复实验。不要只给出“调大数据量”这样的笼统建议。

答案：


### F3. 常见错误判断

判断并修正以下说法：

1. `model.eval()` 会关闭梯度计算。
2. `torch.no_grad()` 会让 Dropout 自动切换成验证行为。
3. 训练时先调用 `softmax` 再传给 `CrossEntropyLoss` 是更规范的做法。
4. 只保存模型权重就足以恢复训练。
5. batch size 加倍后，学习率不需要重新考虑。
6. 验证集准确率提升就说明模型已经泛化良好。
7. 固定一个随机种子后，实验结果就不需要报告方差。
8. checkpoint 文件能加载成功，就说明恢复训练一定正确。

答案：


### F4. 训练闭环排错清单

模型训练“完全不学习”时，请按从数据到优化器的顺序写出排查清单。至少包含：

- 数据和标签可视化；
- 输入范围和 dtype；
- 标签编码与 loss 约定；
- 模型输出 shape；
- 参数是否注册；
- 梯度是否存在且有限；
- 学习率和 optimizer；
- train/eval 模式；
- checkpoint 是否误加载；
- 训练集上能否过拟合极小样本。

答案：


## G. 本周验收

完成本文件和代码实验后，请用自己的话回答：

1. 我能否解释 tensor、计算图、leaf tensor、`requires_grad` 和梯度累积？
2. 我能否独立实现符合 `Dataset`/`DataLoader` 约定的数据输入管线？
3. 我能否写出包含训练、验证、指标统计和 device 管理的完整 PyTorch loop？
4. 我能否解释 `train()`、`eval()`、`no_grad()` 和 `inference_mode()` 的区别？
5. 我能否保存并恢复模型、优化器、scheduler、配置和随机状态？
6. 我能否从 loss/accuracy/梯度曲线判断过拟合、学习率不合适或数据标签错误？
7. 我是否完成了 CIFAR-10 的可复现实验，并比较至少多个超参数或随机种子？
8. 我的 checkpoint 恢复实验是否与不中断对照实验进行了定量比较？
9. 我还不理解或需要继续验证的地方是什么？

答案：

