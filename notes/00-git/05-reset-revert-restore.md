# 05 reset / revert / restore

这三个命令都和“撤销”有关，但作用位置不同。

## restore

用于恢复工作区或暂存区文件。

```bash
git restore README.md
git restore --staged README.md
```

## reset

移动当前分支指针，常用于本地历史整理。

```bash
git reset --soft HEAD~1
git reset --mixed HEAD~1
git reset --hard HEAD~1
```

注意：`--hard` 会丢弃工作区变化，使用前必须确认没有重要内容。

## revert

创建一个新的提交，用来抵消某个旧提交。适合已经共享的历史。

```bash
git revert <commit>
```

## 快速判断

- 只是文件改坏了：优先看 `restore`。
- 本地刚提交错了，还没分享：可以看 `reset`。
- 已经推送出去，需要公开撤销：优先用 `revert`。
