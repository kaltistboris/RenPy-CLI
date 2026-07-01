---
name: renpy-cli
description: >
  通过 CLI 运行、检查、编译和构建 Ren'Py 视觉小说项目。
  当处理 .rpy 脚本、调试 Ren'Py 语法、搭建 Ren'Py 项目、
  构建分发版或操作 Ren'Py 游戏时使用。
---

# Ren'Py CLI Skill

## 概述

本 Skill 让 AI Agent（GitHub Copilot / Claude Code / Codex CLI）能够通过 `renpy` CLI 直接操控 Ren'Py 项目，覆盖日常开发到发布的全流程。

---

## SDK 自动发现

Agent 按以下优先级查找 Ren'Py SDK 路径：

### 1. 路径缓存（最快）
读取 `~/.renpy-cli.json`：

```json
{
  "sdk_path": "D:\\RenPy\\renpy-8.5.3-sdk",
  "renpy_exe": "D:\\RenPy\\renpy-8.5.3-sdk\\renpy.exe",
  "detected_at": "2026-07-01"
}
```

如果该文件存在，直接使用其中的 `renpy_exe` 路径，跳过后续搜索。

### 2. 用户显式指定
用户在对话中提到 Ren'Py 路径时，优先采用。

### 3. 常见安装路径（按 OS）

| 系统 | 路径 |
|------|------|
| Windows | `C:\Program Files\RenPy\renpy-*-sdk\renpy.exe` |
| Windows | `D:\RenPy\renpy-*-sdk\renpy.exe` |
| Windows | `%LOCALAPPDATA%\Microsoft\WinGet\Packages\RenPy.RenPySDK_*\renpy.exe` |
| macOS | `/Applications/Ren'Py.app/Contents/MacOS/renpy` |
| macOS | `~/renpy-*-sdk/renpy.sh` |
| Linux | `~/renpy-*-sdk/renpy.sh` |

### 4. 全局搜索
使用 `file_search` / `find` 搜索 `*renpy*.exe` 或 `renpy.sh`。

### 5. 引导下载
以上均找不到时，引导用户访问 [renpy.org](https://www.renpy.org) 下载 SDK。

---

## CLI 命令参考

```bash
# 基本格式
renpy <项目路径> <命令>

# Windows 示例
"D:\RenPy\renpy-8.5.3-sdk\renpy.exe" D:\MyProject run
```

| 命令 | 用途 | 说明 |
|------|------|------|
| `run` | 启动游戏 | 运行 Ren'Py 项目，进入游戏界面 |
| `lint` | 语法检查 | 检查 .rpy 语法错误、翻译完整性、死代码、未使用的变量等 |
| `compile` | 编译 | 将 .rpy 源代码编译为 .rpyc 字节码 |
| `distribute` | 构建分发版 | 生成可分发的游戏包（Windows / macOS / Linux 版） |
| `quit` | 退出游戏 | 发送退出信号到运行中的 Ren'Py 进程 |
| `screenshot` ⚡ | 截图 | 通过 `scripts/screenshot.py` 捕获游戏窗口画面，用于 AI 视觉分析 |

### lint 常见输出解读

- **"unused variable"**：定义了但未使用的变量，建议删除或用 `_` 前缀
- **"missing translation"**：语言文件缺少对应翻译条目
- **"style not defined"**：引用了未定义的样式
- **"dead code"**：永远不会被执行到的代码块
- **"could not find label"**：跳转目标标签不存在

---

## 常用工作流

### 1. 创建新项目

```bash
# Ren'Py SDK 自带项目创建向导，通过 launcher 启动
renpy <sdk_path> launcher

# 也可以在 SDK 目录下手动创建项目结构
mkdir MyProject/game/
```

### 2. 日常开发循环

```
编辑 .rpy → lint 检查 → run 测试
```

```bash
# 第 1 步：检查语法
renpy <project_path> lint

# 第 2 步：运行测试
renpy <project_path> run
```

### 3. 发布前检查

```
lint → compile → distribute
```

```bash
# 第 1 步：完整检查
renpy <project_path> lint

# 第 2 步：编译为字节码
renpy <project_path> compile

# 第 3 步：构建分发版
renpy launcher distribute <project_path>
```

### 4. 画面截图（调试/视觉分析）

启动游戏，等待窗口就绪后截取当前画面，用于 AI 视觉分析或文档记录。

```bash
# 启动并截图（自动退出游戏）
uv run python scripts/screenshot.py ^
    --sdk "D:\RenPy\renpy-8.5.3-sdk" ^
    --project D:\MyProject ^
    --output screenshot.png

# 附加到已在运行的游戏截图
uv run python scripts/screenshot.py --attach --output screenshot.png
```

**脚本功能**：
- 启动 Ren'Py 项目并等待窗口就绪（超时控制）
- 自动检测窗口类名 `SDL_app`，过滤离屏/无效窗口
- 截取游戏客户区画面（PNG 格式）
- 截图完成后自动发送 `quit` 命令关闭游戏
- 支持 `--attach` 附加到已在运行的 Ren'Py 游戏

> **依赖**：需要 `pywin32` 和 `Pillow`，项目已通过 `uv add pywin32 Pillow` 配置。

---

## VS Code 集成

### 使用 setup-tasks.py 生成 tasks.json

在项目目录下运行：

```bash
python scripts/setup-tasks.py
```

会自动检测 Ren'Py SDK 路径并生成 `.vscode/tasks.json`，包含以下任务：

| 任务名 | 命令 | 快捷键 |
|--------|------|--------|
| Ren'Py: Run | `python run_renpy.py <sdk> <project> run` | `Ctrl+Shift+B` (build) |
| Ren'Py: Lint | `python run_renpy.py <sdk> <project> lint` | — |
| Ren'Py: Compile | `python run_renpy.py <sdk> <project> compile` | — |
| Ren'Py: Distribute | `python run_renpy.py <sdk> launcher distribute <project>` | — |
| Ren'Py: Screenshot | `uv run python scripts/screenshot.py --sdk <sdk> --project <project> --output .vscode/screenshot.png` | — |

> **注**：生成的 tasks 通过 `scripts/run_renpy.py` 封装器调用 Ren'Py CLI。这是因为 `renpy.exe` 是 Windows GUI 程序，直接 shell 调用无法在终端中显示 stdout/stderr 输出。`run_renpy.py` 使用 Python `subprocess` 捕获输出，确保 lint/compile 的结果在 VS Code 终端可见。

### 手动配置 tasks.json

如果不想用脚本，也可以手动创建 `.vscode/tasks.json`，参考 `scripts/setup-tasks.py` 的输出格式。注意 lint/compile 等需要输出捕获的任务应通过 `run_renpy.py` 封装。

---

## 故障排查

### 找不到 renpy 命令

```
错误信息：'renpy' 不是内部或外部命令，也不是可运行的程序
```

**原因**：Ren'Py SDK 不在 PATH 中，不能直接用 `renpy` 命令。

**解决**：始终使用完整路径调用，例如：
```bash
"D:\RenPy\renpy-8.5.3-sdk\renpy.exe" <project_path> lint
```

### Windows 下无终端输出

```
（命令执行成功但终端没有任何输出）
```

**原因**：`renpy.exe` 是 Windows GUI 子系统程序，从终端（bash/cmd）直接运行时，其 stdout/stderr **不会**连接到当前终端，导致输出不可见。但命令本身仍正常执行（可通过退出码判断）。

**解决**：用 Python 的 `subprocess` 捕获输出：
```python
import subprocess
result = subprocess.run(
    ["renpy.exe", "project_path", "lint"],
    capture_output=True, text=True, timeout=30
)
print(result.stdout)
```

或在 PowerShell 中用 `Start-Process` 的 `-Wait` 参数，或直接查看 Ren'Py 生成的日志文件。

### 路径包含空格

```
错误信息：cannot find project
```

**解决**：始终用双引号包裹路径，特别是 `Program Files` 或带空格的游戏项目名。

### 项目路径错误

```
错误信息：could not find project
```

**注意**：项目路径应指向包含 `game/` 子目录的文件夹，而不是 `game/` 本身。

### lint 报错太多

```bash
# 只关注错误（忽略警告）
renpy <project_path> lint 2>&1 | findstr /i "error"

# 分步检查：先修语法错误，再修警告
```

---

## 脚本工具一览

| 脚本 | 用途 |
|------|------|
| `scripts/setup-tasks.py` | 生成 VS Code tasks.json |
| `scripts/run_renpy.py` | Ren'Py CLI 封装器（解决 Windows 输出捕获） |
| `scripts/screenshot.py` | Ren'Py 游戏窗口截图工具 |

---

## 跨 Agent 兼容说明

| Agent | 加载方式 | 执行命令方式 |
|-------|---------|-------------|
| **GitHub Copilot** | `description` 关键词匹配 → 自动加载 | `run_in_terminal` |
| **Claude Code** | 检测任务 → 读取 `~/.claude/skills/renpy-cli/` | `Bash` 工具 |
| **Codex CLI** | 读取 SKILL.md 作为系统指令 | `shell` 命令 |

所有命令示例使用纯 shell 语法，各 Agent 自行翻译为对应的工具调用。
