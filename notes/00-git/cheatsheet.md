# Git Cheatsheet

## 查看状态

```bash
git status
git log --oneline --graph --decorate --all
git diff
git diff --staged
```

## 提交

```bash
git add <file>
git commit -m "type: short description"
```

## 分支

```bash
git branch
git switch -c <branch>
git switch <branch>
git merge <branch>
git branch -d <branch>
```

## 撤销

```bash
git restore <file>
git restore --staged <file>
git reset --soft HEAD~1
git revert <commit>
```

## 远程

```bash
git remote -v
git remote add origin <url>
git push -u origin main
git pull --rebase
```

## 建议提交类型

- `docs:` 文档和笔记
- `lab:` 练习代码或实验
- `project:` 阶段项目
- `fix:` 修复错误
- `chore:` 仓库维护
