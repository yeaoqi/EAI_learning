# 03 conflict

## 冲突是什么

当两个分支修改了同一文件的同一位置，Git 无法自动判断保留哪一边，就会产生冲突。

## 冲突标记

```text
<<<<<<< HEAD
当前分支的内容
=======
被合并分支的内容
>>>>>>> lesson/conflict-demo
```

解决冲突时，不是简单删除标记，而是重新整理成最终应该保留的内容。

## 常用命令

```bash
git status
git diff
git add path/to/file.md
git commit
```

## 练习

在 [labs/git-playground](../../labs/git-playground) 中完成一次冲突制造和解决。

## 复盘问题

- 冲突发生在哪个文件？
- 两边修改的真实意图分别是什么？
- 最终内容为什么这样保留？
