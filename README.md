# Ren'Py CLI Skill

让 AI Agent（GitHub Copilot / Claude Code / Codex CLI）通过 CLI 直接操控 Ren'Py 项目——运行、检查、编译、构建，一步到位。

---

## 安装

### 方式一：GitHub Copilot

```bash
# 将仓库克隆到 Copilot Skills 目录
git clone https://github.com/<你的用户名>/renpy-cli.git "%USERPROFILE%\.copilot\skills\renpy-cli"
```

Copilot 会在处理 Ren'Py 相关任务时自动加载本 Skill。

### 方式二：Claude Code

```bash
git clone https://github.com/<你的用户名>/renpy-cli.git ~/.claude/skills/renpy-cli
```

### 方式三：手动复制

将整个仓库复制到对应 Agent 的 skills 目录即可。

---

## 前置要求

1. **Ren'Py SDK**：从 [renpy.org](https://www.renpy.org) 下载并安装
2. **Python 3.8+**（可选）：用于运行 `scripts/setup-tasks.py`

---

## 使用方法

### 在 VS Code 中一键运行/检查

在项目目录下运行：

```bash
python scripts/setup-tasks.py
```

会自动生成 `.vscode/tasks.json`，之后按 `Ctrl+Shift+B` 即可运行项目。

### 常用命令速查

```bash
# 语法检查
renpy <sdk_path>/renpy.exe <project_path> lint

# 运行游戏
renpy <sdk_path>/renpy.exe <project_path> run

# 编译
renpy <sdk_path>/renpy.exe <project_path> compile

# 构建分发版
renpy <sdk_path>/renpy.exe launcher distribute <project_path>
```

### 与 AI Agent 配合

在对话中告诉 Agent：

> "帮我 lint 一下这个 Ren'Py 项目"
> "检查 .rpy 文件里的语法错误"
> "构建一个 Windows 分发版"

Agent 会自动调用本 Skill 中的知识来完成操作。

---

## 项目结构

```
renpy-cli/
├── SKILL.md                        ← AI Agent 读取的主技能文件
├── README.md                       ← 本文件
├── scripts/
│   ├── setup-tasks.py              ← 为项目生成 VS Code tasks.json
│   └── run_renpy.py                ← Ren'Py CLI 封装器（解决 Windows 输出捕获）
├── templates/
│   └── renpy-docs.instructions.md  ← 可复用的"文档优先"工作区指令
├── .gitignore
└── LICENSE
```

---

## 原理

本 Skill 不安装任何额外工具，而是利用 **Ren'Py SDK 自带的 CLI 工具**，将 AI Agent 能理解的操作（运行、检查、编译、构建）映射为对应的 `renpy` 命令。

Agent 加载 `SKILL.md` 后，会自动学习：
- 如何发现本机 Ren'Py SDK 路径
- 各 CLI 命令的功能和用法
- 标准开发工作流
- 常见故障排查方法

---

## 许可证

MIT
