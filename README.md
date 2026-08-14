# 具身智能学习仓库

这是一个面向具身智能方向的长期学习仓库，同时也是 Git 学习与复习练习场。仓库当前围绕一条 52 周路线组织：从数学、机器人学、深度学习、ROS 2 与仿真，逐步走到模仿学习、VLA、真机部署和研究产出。

## 在线入口

- 学习控制台：[docs/index.html](docs/index.html)
- 总路线图：[ROADMAP.md](ROADMAP.md)
- Git 学习笔记：[notes/00-git](notes/00-git)
- Git 练习场：[labs/git-playground](labs/git-playground)

如果托管到 GitHub，可以在仓库设置里启用 GitHub Pages，并选择 `docs/` 目录作为发布源。

## 仓库结构

```text
.
├─ docs/                 # 可分享网页、图片和静态资源
├─ notes/                # 按主题沉淀的复习笔记
├─ labs/                 # 可运行练习与 Git 操作演示
├─ projects/             # 阶段验收成果
├─ templates/            # 周复盘、实验日志、论文阅读等模板
├─ ROADMAP.md            # 52 周学习路线总览
└─ CHANGELOG.md          # 学习与仓库变更记录
```

## 推荐使用方式

1. 每周从 `docs/index.html` 或 `ROADMAP.md` 找到当前任务。
2. 学习笔记写到 `notes/`，实验和代码写到 `labs/` 或 `projects/`。
3. 每次完成一个清晰的小目标就提交一次 Git commit。
4. 每周用 [templates/weekly-review.md](templates/weekly-review.md) 做复盘。
5. 阶段验收成果放到 `projects/milestone-*`，方便之后展示和分享。

## Git 学习路线

建议把这个仓库本身当作练习对象：

1. `init/add/commit/status/log`：建立基本版本感。
2. `branch/merge`：用分支记录不同学习任务。
3. `conflict`：在 `labs/git-playground` 里故意制造并解决冲突。
4. `restore/reset/revert`：学习撤销、回退和反悔。
5. `rebase/cherry-pick/tag`：整理历史并标记阶段成果。
6. `remote/pull request`：把本地学习仓库变成可分享项目。

## 命名约定

- 分支：`lesson/git-branch-merge`、`week/01-svd`、`project/w08-basic-gate`
- 标签：`w01-done`、`w08-basic-gate`、`git-conflict-demo`
- 提交信息：`docs: add week 01 notes`、`lab: practice merge conflict`

## 许可证

当前仓库暂未选择正式开源许可证。公开分享前建议明确采用 MIT、Apache-2.0、CC BY 4.0 或其他适合你目标的许可证。
