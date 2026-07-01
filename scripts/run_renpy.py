"""
Ren'Py CLI 封装器 - 解决 Windows GUI 程序输出捕获问题

用法：
    python run_renpy.py <sdk_exe> <project_path> <command> [args...]

示例：
    python run_renpy.py "D:\\RenPy\\renpy-8.5.3-sdk\\renpy.exe" "D:\\Project" lint
    python run_renpy.py "D:\\RenPy\\renpy-8.5.3-sdk\\renpy.exe" "D:\\Project" run
    python run_renpy.py "D:\\RenPy\\renpy-8.5.3-sdk\\renpy.exe" launcher distribute "D:\\Project"
"""

import subprocess
import sys


def main():
    if len(sys.argv) < 4:
        print(f"用法: {sys.argv[0]} <sdk_exe> <project_or_launcher> <command> [args...]")
        sys.exit(1)

    sdk_exe = sys.argv[1]
    project_or_launcher = sys.argv[2]
    command = sys.argv[3]

    # 构建 renpy 参数
    # 处理 launcher 命令的特殊格式: renpy launcher distribute <project>
    if project_or_launcher == "launcher":
        args = [sdk_exe, "launcher", command] + sys.argv[4:]
    else:
        args = [sdk_exe, project_or_launcher, command] + sys.argv[4:]

    # 对于 lint/compile，捕获输出并打印
    # 对于 run，不捕获（游戏需要自己的窗口）
    if command in ("lint", "compile"):
        result = subprocess.run(args, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    else:
        # run / distribute / quit — 不捕获输出
        result = subprocess.run(args)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
