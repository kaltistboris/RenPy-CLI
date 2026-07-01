"""
Ren'Py 游戏窗口截图工具

对正在运行或新启动的 Ren'Py 游戏窗口进行截图，
支持等待窗口就绪和超时控制。

用法：
    # 启动项目并截图（自动退出）
    uv run python scripts/screenshot.py ^
        --sdk D:\\RenPy\\renpy-8.5.3-sdk ^
        --project D:\\MyRenPyGame ^
        --output screenshot.png

    # 附加到已在运行的 Ren'Py 游戏
    uv run python scripts/screenshot.py --attach --output screenshot.png

    # 启动并保持运行（仅截图不退出）
    uv run python scripts/screenshot.py ^
        --sdk D:\\RenPy\\renpy-8.5.3-sdk ^
        --project D:\\MyRenPyGame ^
        --output screenshot.png --no-quit
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

try:
    import win32gui
    import win32ui
    import win32con
    import win32api
except ImportError:
    print("错误: 需要 pywin32 库。请运行: uv add pywin32")
    sys.exit(1)

RENPY_WINDOW_CLASS = "SDL_app"
POLL_INTERVAL = 0.5  # 秒


# ── 窗口查找 ──────────────────────────────────────────

def _is_valid_window(hwnd: int) -> bool:
    """判断窗口是否有效（可见、有标题、在屏幕范围内）。"""
    if not win32gui.IsWindowVisible(hwnd):
        return False
    try:
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        # 排除离屏窗口（坐标过负或为零）
        if width <= 0 or height <= 0:
            return False
        if rect[0] < -10000 or rect[1] < -10000:
            return False
        # 排除系统托盘等极小的窗口
        if width < 100 and height < 100:
            return False
        return True
    except Exception:
        return False


def find_renpy_window(timeout: float = 30.0) -> int | None:
    """等待并返回 Ren'Py 游戏窗口的 HWND。

    按类名 SDL_app 查找可见的有效窗口，轮询直到超时。
    返回窗口句柄，超时返回 None。
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        candidates = []

        def enum_cb(hwnd: int, results: list):
            if win32gui.IsWindowVisible(hwnd):
                cls = win32gui.GetClassName(hwnd)
                if cls == RENPY_WINDOW_CLASS and _is_valid_window(hwnd):
                    results.append(hwnd)

        win32gui.EnumWindows(enum_cb, candidates)

        if candidates:
            # 取面积最大的 SDL_app 窗口（排除非游戏 SDL 窗口）
            best = max(candidates, key=lambda h: _window_area(h))
            return best

        time.sleep(POLL_INTERVAL)

    return None


def _window_area(hwnd: int) -> int:
    """计算窗口面积。"""
    try:
        rect = win32gui.GetWindowRect(hwnd)
        return (rect[2] - rect[0]) * (rect[3] - rect[1])
    except Exception:
        return 0


# ── 截图 ──────────────────────────────────────────────

def capture_window(hwnd: int) -> Image.Image:
    """捕获指定窗口客户区内容为 PIL Image。"""
    # 获取客户区矩形
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        raise RuntimeError(f"窗口尺寸无效: {width}x{height}")

    # 客户区在屏幕上的绝对偏移
    client_pt = win32gui.ClientToScreen(hwnd, (0, 0))

    # 获取窗口 DC（仅客户区）
    hwnd_dc = win32gui.GetDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # 创建兼容位图
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    old_bitmap = save_dc.SelectObject(bitmap)

    # BitBlt 复制像素（从客户区原点拷贝）
    save_dc.BitBlt(
        (0, 0), (width, height),
        mfc_dc,
        (0, 0),
        win32con.SRCCOPY,
    )

    # 转换为 PIL Image
    bmp_info = bitmap.GetInfo()
    bmp_str = bitmap.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGB",
        (bmp_info["bmWidth"], bmp_info["bmHeight"]),
        bmp_str,
        "raw",
        "BGRX",
        0,
        1,
    )

    # 清理
    save_dc.SelectObject(old_bitmap)
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    win32gui.DeleteObject(bitmap.GetHandle())

    return img


# ── 游戏进程管理 ──────────────────────────────────────

def launch_game(sdk_path: Path, project_path: Path) -> subprocess.Popen | None:
    """启动 Ren'Py 游戏，返回进程对象。"""
    exe = sdk_path / "renpy.exe"
    if not exe.exists():
        print(f"错误: 未找到 {exe}")
        return None

    print(f"🚀 启动游戏: {project_path.name}...")
    return subprocess.Popen(
        [str(exe), str(project_path), "run"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def quit_game(sdk_path: Path, project_path: Path) -> None:
    """向 Ren'Py 游戏发送 quit 命令。"""
    exe = sdk_path / "renpy.exe"
    if exe.exists():
        subprocess.run(
            [str(exe), str(project_path), "quit"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )


# ── 主流程 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ren'Py 游戏窗口截图")
    parser.add_argument("--sdk", help="Ren'Py SDK 路径")
    parser.add_argument("--project", "-p", help="Ren'Py 项目路径")
    parser.add_argument("--output", "-o", default="renpy_screenshot.png", help="输出图片路径")
    parser.add_argument("--timeout", "-t", type=float, default=30.0, help="等待窗口超时秒数")
    parser.add_argument("--attach", action="store_true", help="附加到已在运行的窗口，不启动新游戏")
    parser.add_argument("--no-quit", action="store_true", help="截图后不关闭游戏")
    args = parser.parse_args()

    # ── 启动或附加 ──
    proc = None
    if not args.attach:
        if not args.sdk or not args.project:
            parser.error("--attach 模式下需要 --sdk 和 --project")
        sdk_path = Path(args.sdk)
        proj_path = Path(args.project)
        proc = launch_game(sdk_path, proj_path)
        if proc is None:
            sys.exit(1)
        print(f"  PID: {proc.pid}")
    else:
        print("🔗 附加到已运行的 Ren'Py 游戏...")

    # ── 等待窗口就绪 ──
    print(f"⏳ 等待窗口就绪（超时 {args.timeout:.0f}s）...")
    hwnd = find_renpy_window(timeout=args.timeout)

    if hwnd is None:
        print("❌ 超时: 未检测到 Ren'Py 游戏窗口")
        if proc:
            proc.kill()
        sys.exit(1)

    title = win32gui.GetWindowText(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    print(f"  ✓ 找到窗口: \"{title}\"  HWND={hwnd}  Size={rect[2]-rect[0]}x{rect[3]-rect[1]}")

    # ── 截图 ──
    print("📸 截图...")
    try:
        img = capture_window(hwnd)
        output_path = Path(args.output)
        img.save(output_path)
        print(f"  ✓ 已保存: {output_path.resolve()}  ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        if proc:
            proc.kill()
        sys.exit(1)

    # ── 退出 ──
    if not args.no_quit:
        if args.sdk and args.project:
            print("🔚 关闭游戏...")
            quit_game(Path(args.sdk), Path(args.project))
        if proc:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("  ✓ 已退出")
    else:
        print("  ➡ 游戏保持运行（--no-quit）")


if __name__ == "__main__":
    main()
