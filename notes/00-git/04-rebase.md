# 04 rebase

## rebase 解决什么问题

`rebase` 可以把当前分支的提交搬到另一条提交历史之后，让历史更线性。它适合整理自己的本地分支，不适合随意改写已经共享给别人的公共历史。

## 常用命令

```bash
git switch feature/topic
git fetch
git rebase main
git rebase --continue
git rebase --abort
```

## 交互式整理提交

```bash
git rebase -i HEAD~3
```

常见动作：

- `pick`：保留提交
- `reword`：修改提交信息
- `squash`：合并到前一个提交
- `drop`：删除提交

## 判断是否应该 rebase

- 只是自己的本地练习分支：可以。
- 已经推送并且别人可能基于它继续开发：谨慎。
- 不理解当前状态：先 `git status`，必要时先备份分支。
