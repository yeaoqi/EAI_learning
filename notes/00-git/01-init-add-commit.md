# 01 init / add / commit

## 核心概念

- 工作区：正在编辑但不一定准备提交的文件。
- 暂存区：下一次 commit 会包含的快照。
- 本地仓库：已经提交的历史记录。

## 常用命令

```bash
git init
git status
git add README.md
git add .
git commit -m "docs: initialize repository"
git log --oneline
```

## 练习

1. 修改 `README.md`。
2. 用 `git diff` 查看未暂存变化。
3. 用 `git add README.md` 放入暂存区。
4. 用 `git diff --staged` 查看即将提交的变化。
5. 提交并用 `git log --oneline` 检查历史。

## 易错点

- `git add .` 不是提交，只是把变化放进暂存区。
- commit 应该表达一个清晰意图，不建议把很多无关变化塞进同一次提交。
