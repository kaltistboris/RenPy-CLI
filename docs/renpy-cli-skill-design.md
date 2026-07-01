# Ren'Py CLI Skill — 设计方案

> 目标：做一个跨 AI Agent（Copilot / Claude Code / Codex CLI）通用的 Ren'Py 开发 Skill，让 Agent 能通过 CLI 直接操控 Ren'Py 项目（运行、检查、编译、构建）。

---

## 一、对标参考

| | Playwright Skill | Ren'Py CLI Skill |
|---|---|---|
| CLI 工具 | `playwright-cli` | `renpy`（Ren'Py SDK 自带） |
| 核心操作 | open / goto / click / snapshot | run / lint / compile / distribute |
| 安装方式 | npm 包 | 官网下载 SDK |
| Skill 文件 | `SKILL.md` | `SKILL.md` |
| 适用 Agent | Copilot / Claude Code | Copilot / Claude Code / Codex CLI |

---

## 二、文件结构

```
renpy-cli/                        ← 仓库根目录
├── SKILL.md                      ← 主技能文件（Agent 读取入口）
├── README.md                     ← 人类看的说明 + 安装指引
├── scripts/
│   └── setup-tasks.py            ← 给项目生成 .vscode/tasks.json
├── templates/
│   └── renpy-docs.instructions.md ← 可复用的"文档优先"工作区指令
└── LICENSE
```

### 用户安装方式

```bash
# Copilot
git clone https://github.com/xxx/renpy-cli.git ~/.copilot/skills/renpy-cli

# Claude Code
git clone https://github.com/xxx/renpy-cli.git ~/.claude/skills/renpy-cli
```

---

## 三、SKILL.md 大纲

```markdown
---
name: renpy-cli
description: >
  Run, lint, compile, and build Ren'Py visual novel projects from CLI.
  Use when developing .rpy scripts, debugging Ren'Py syntax, setting up
  a Ren'Py project, building distributions, or working with Ren'Py games.
---

# Ren'Py CLI

## 自动发现 Ren'Py SDK

（给 Agent 的查找逻辑 — 按 OS 枚举常见安装路径）

### Windows
- `C:\Program Files\RenPy\renpy-<version>-sdk\renpy.exe`
- `D:\RenPy\renpy-<version>-sdk\renpy.exe`
- winget 安装：`%LOCALAPPDATA%\Microsoft\WinGet\Packages\RenPy.RenPySDK_*\renpy.exe`

### macOS
- `/Applications/Ren'Py.app/Contents/MacOS/renpy`
- `~/renpy-<version>-sdk/renpy.sh`

### Linux
- `~/renpy-<version>-sdk/renpy.sh`

## CLI 命令参考

| 命令 | 用途 |
|------|------|
| `renpy <project> run` | 启动游戏 |
| `renpy <project> lint` | 检查 .rpy 语法/翻译/死代码 |
| `renpy <project> compile` | 编译 .rpy → .rpyc |
| `renpy launcher distribute <project>` | 构建分发版 |
| `renpy <project> quit` | 退出游戏 |

## 常用工作流

### 1. 创建新项目
### 2. 日常开发循环（编辑→lint→run）
### 3. 发布前检查（lint→compile→distribute）

## VS Code 集成
（如何用 setup-tasks.py 生成 tasks.json）

## 故障排查
（常见问题：找不到 renpy、权限、路径空格）
```

---

## 四、核心设计决策

### 4.1 Ren'Py 路径发现策略

不依赖环境变量/注册表（不可靠），而是让 Agent 按优先级搜索：

```
1. 用户显式指定的路径（如对话中提到）
2. 常见安装路径（见上表）
3. file_search 搜索 *renpy*.exe / renpy.sh
4. 找不到时 → 引导用户去 renpy.org 下载
```

### 4.2 跨 Agent 兼容

| Agent | 加载方式 | 工具调用 |
|-------|---------|---------|
| **GitHub Copilot** | `description` 关键词匹配 → 自动加载 SKILL.md | `run_in_terminal` |
| **Claude Code** | 检测到 Ren'Py 任务 → 加载 `~/.claude/skills/renpy-cli/` | `Bash` |
| **Codex CLI** | 读取 SKILL.md 作为系统指令 | `shell` |

关键：SKILL.md 里的命令示例要用**纯 shell 语法**（不依赖特定 Agent 的工具名），让各 Agent 自己翻译成对应的工具调用。

### 4.3 与其他自定义项的关系

```
~/.copilot/skills/renpy-cli/SKILL.md     ← [本 Skill] 通用 CLI 操控
项目/.github/instructions/renpy-docs.instructions.md  ← [工作区级] 文档优先
项目/.vscode/tasks.json                   ← [可选] scripts/setup-tasks.py 生成
```

---

## 五、Phase 1 MVP 范围

- [x] 设计文档（本文）
- [ ] 创建 SKILL.md
- [ ] 创建 README.md（安装说明）
- [ ] 创建 `scripts/setup-tasks.py`
- [ ] 创建 `templates/renpy-docs.instructions.md`
- [ ] 发布到 GitHub
- [ ] 在本机安装测试（WuRongBai 项目）

---

## 六、Phase 2 展望（Plan B 保留）

- [ ] 封装为 npm 包：`npx renpy-cli setup` 一键初始化项目
- [ ] pip 包：`pip install renpy-cli`（因为目标用户基本都装 Python）
- [ ] VS Code 扩展：侧边栏按钮 → 一键 Run / Lint / Build
- [ ] MCP Server：Agent 通过 MCP 协议直接调用 Ren'Py API

---

## 七、待讨论

1. **安装路径发现**：要不要做一个安装脚本，把路径写到 `~/.renpy-cli.json` 里，避免 Agent 每次都搜？
2. **setup-tasks.py 的触发方式**：Agent 自动检测到 Ren'Py 项目就生成？还是由用户手动说"初始化 Ren'Py 项目"？
3. **是否需要 `allowed-tools` 限制**：对 Claude Code 来说加 `allowed-tools: Bash(renpy:*)` 更安全，但 Copilot 不认这个字段。
