# Git 练习场

这个目录专门用于制造安全的 Git 练习。这里的文件可以大胆改、提交、分支、合并和回滚。

## 练习 1：第一次提交

1. 新建一个 `hello-git.md`。
2. 写下今天学习 Git 的目标。
3. 使用 `git add` 和 `git commit` 提交。

## 练习 2：分支合并

```bash
git switch -c lesson/git-branch-merge
```

1. 修改本目录下任意文件。
2. 提交。
3. 切回 `main`。
4. 执行 `git merge lesson/git-branch-merge`。

## 练习 3：制造冲突

1. 在 `main` 修改同一行文字并提交。
2. 新建或切换到另一个分支，修改同一行文字并提交。
3. 回到 `main` 合并该分支。
4. 按照冲突标记整理最终内容。
5. `git add` 后完成合并提交。

## 练习 4：撤销

依次练习：

- `git restore`
- `git restore --staged`
- `git reset --soft HEAD~1`
- `git revert <commit>`

每次练习后都写一句复盘：这次命令改变了工作区、暂存区还是提交历史？
