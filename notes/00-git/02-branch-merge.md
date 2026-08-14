# 02 branch / merge

## 核心概念

分支是指向某个提交的可移动指针。使用分支可以把不同任务隔离开，等任务完成后再合并回主线。

## 常用命令

```bash
git branch
git switch -c lesson/git-branch-merge
git switch main
git merge lesson/git-branch-merge
git branch -d lesson/git-branch-merge
```

## 推荐分支命名

- `lesson/git-branch-merge`
- `week/01-svd`
- `project/w08-basic-gate`
- `fix/readme-link`

## 练习

1. 新建一个 `lesson/git-branch-merge` 分支。
2. 修改一份 Git 笔记并提交。
3. 切回 `main`。
4. 合并该分支。
5. 删除已经合并的练习分支。
