"""
Ren'Py CLI - VS Code tasks.json 生成器

检测本机 Ren'Py SDK 路径，为当前项目生成 .vscode/tasks.json，
包含 Run / Lint / Compile / Distribute 四个任务。

用法：
    python scripts/setup-tasks.py
    python scripts/setup-tasks.py --sdk-path "D:\RenPy\renpy-8.5.3-sdk"
"""

import json
import os
import sys
import glob
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────
CACHE_FILE = Path.home() / ".renpy-cli.json"
TASKS_FILE = ".vscode" / Path("tasks.json")

COMMON_WINDOWS_PATTERNS = [
    r"C:\Program Files\RenPy\renpy-*-sdk\renpy.exe",
    r"D:\RenPy\renpy-*-sdk\renpy.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\RenPy.RenPySDK_*\renpy.exe"),
]


# ── SDK 发现 ──────────────────────────────────────────

def find_from_cache() -> Path | None:
    """从 ~/.renpy-cli.json 读取缓存路径。"""
    if not CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        exe = Path(data["renpy_exe"])
        if exe.exists():
            return exe
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def find_from_common_paths() -> Path | None:
    """枚举常见安装路径。"""
    for pattern in COMMON_WINDOWS_PATTERNS:
        matches = glob.glob(pattern)
        if matches:
            exe = Path(matches[0])
            if exe.exists():
                return exe
    return None


def find_renpy_sdk() -> Path | None:
    """按优先级查找 Ren'Py SDK 可执行文件路径。"""
    # 1. 缓存
    cached = find_from_cache()
    if cached:
        return cached

    # 2. 常见路径
    common = find_from_common_paths()
    if common:
        return common

    return None


def save_cache(exe_path: Path) -> None:
    """保存 SDK 路径到缓存文件。"""
    data = {
        "sdk_path": str(exe_path.parent),
        "renpy_exe": str(exe_path),
        "detected_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ 已缓存 SDK 路径到 {CACHE_FILE}")


def prompt_user_for_sdk() -> Path | None:
    """交互式询问用户 SDK 路径。"""
    print("  ⚠ 未找到 Ren'Py SDK。")
    print("    请从 https://www.renpy.org 下载并安装。")
    path = input("  → 输入 Ren'Py SDK 路径（如 D:\\RenPy\\renpy-8.5.3-sdk）: ").strip()
    if not path:
        return None

    exe_candidates = [
        Path(path) / "renpy.exe",
        Path(path) / "renpy.sh",
    ]
    for exe in exe_candidates:
        if exe.exists():
            return exe

    print(f"  ✗ 未在 {path} 中找到 renpy.exe/renpy.sh")
    return None


# ── 项目检测 ──────────────────────────────────────────

def find_project_root() -> Path | None:
    """从当前目录向上查找包含 game/ 的 Ren'Py 项目根目录。"""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / "game").is_dir():
            return parent
    return None


# ── tasks.json 生成 ───────────────────────────────────

def build_tasks(sdk_exe: Path, project_path: Path) -> list[dict]:
    """构建 VS Code tasks 列表。"""
    sdk_str = str(sdk_exe)
    proj_str = str(project_path)

    return [
        {
            "label": "Ren'Py: Run",
            "type": "shell",
            "command": f'"{sdk_str}" "{proj_str}" run',
            "group": {"kind": "build", "isDefault": True},
            "presentation": {"echo": true, "reveal": "always", "focus": true},
            "problemMatcher": [],
        },
        {
            "label": "Ren'Py: Lint",
            "type": "shell",
            "command": f'"{sdk_str}" "{proj_str}" lint',
            "group": "build",
            "presentation": {"echo": true, "reveal": "always", "focus": false},
            "problemMatcher": [],
        },
        {
            "label": "Ren'Py: Compile",
            "type": "shell",
            "command": f'"{sdk_str}" "{proj_str}" compile',
            "group": "build",
            "presentation": {"echo": true, "reveal": "always", "focus": false},
            "problemMatcher": [],
        },
        {
            "label": "Ren'Py: Distribute",
            "type": "shell",
            "command": f'"{sdk_str}" launcher distribute "{proj_str}"',
            "group": "build",
            "presentation": {"echo": true, "reveal": "always", "focus": false},
            "problemMatcher": [],
        },
    ]


def write_tasks_json(tasks: list[dict], output_path: Path) -> None:
    """写入 .vscode/tasks.json。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = {
        "version": "2.0.0",
        "tasks": tasks,
    }
    output_path.write_text(
        json.dumps(content, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ── 主流程 ────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Ren'Py CLI — VS Code 任务生成器")
    print("=" * 50)
    print()

    # 1. SDK 检测
    print("🔍 检测 Ren'Py SDK...")
    sdk_exe = find_renpy_sdk()

    # 命令行参数覆盖
    if len(sys.argv) > 1 and sys.argv[1] == "--sdk-path" and len(sys.argv) > 2:
        custom_path = Path(sys.argv[2])
        exe = custom_path / "renpy.exe"
        if exe.exists():
            sdk_exe = exe
            print(f"  ✓ 使用命令行指定路径: {exe}")
        else:
            print(f"  ✗ 指定路径下未找到 renpy.exe: {custom_path}")
            sys.exit(1)

    if sdk_exe is None:
        sdk_exe = prompt_user_for_sdk()
        if sdk_exe is None:
            print("\n  ✗ 无法继续，未找到 Ren'Py SDK。")
            print("    下载地址: https://www.renpy.org")
            sys.exit(1)

    print(f"  ✓ 找到 SDK: {sdk_exe}")
    save_cache(sdk_exe)

    # 2. 项目检测
    print()
    print("📂 检测 Ren'Py 项目...")
    project_root = find_project_root()
    if project_root is None:
        print("  ⚠ 当前目录不是 Ren'Py 项目（未找到 game/ 子目录）")
        ans = input("  → 仍要生成 tasks.json？(y/N): ").strip().lower()
        if ans != "y":
            print("  已取消。")
            sys.exit(0)
        project_root = Path.cwd()

    print(f"  ✓ 项目根目录: {project_root}")

    # 3. 生成 tasks.json
    print()
    print("📝 生成 tasks.json...")
    tasks = build_tasks(sdk_exe, project_root)
    output = project_root / TASKS_FILE
    write_tasks_json(tasks, output)
    print(f"  ✓ 已写入: {output}")
    print()

    # 4. 摘要
    print("=" * 50)
    print("  生成完毕！可用任务：")
    for t in tasks:
        print(f"    • {t['label']}: {t['command']}")
    print()
    print("  💡 按 Ctrl+Shift+B 可直接运行 Ren'Py: Run")
    print("=" * 50)


if __name__ == "__main__":
    main()
