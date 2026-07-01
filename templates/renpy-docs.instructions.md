---
name: renpy-docs
description: >
  Ren'Py 项目"文档优先"指令。
  在处理本项目时，先读取项目文档和 Ren'Py 参考文档，
  再进行代码修改或问题排查。
applyTo: "**/*.rpy"
---

# Ren'Py 文档优先指令

## 原则

在修改任何 `.rpy` 文件之前，必须优先读取相关文档，确保对 Ren'Py 语法和项目结构有充分理解。

---

## 1. 项目文档

> 将以下路径替换为实际项目中的文档位置

- **项目 README**：`README.md`
- **项目架构文档**：`docs/architecture.md`（如有）
- **角色/剧情文档**：`docs/characters/`（如有）
- **GUI 设计文档**：`docs/gui/`（如有）

## 2. Ren'Py 官方参考（按需查阅）

| 主题 | 链接 |
|------|------|
| 语言基础 | https://doc.renpy.cn/zh-CN/ |
| 语句（if/while/等） | https://doc.renpy.cn/zh-CN/language_basics.html |
| 转场与动画 | https://doc.renpy.cn/zh-CN/transforms.html |
| 屏幕语言（Screen Language） | https://doc.renpy.cn/zh-CN/screens.html |
| 音频/视频 | https://doc.renpy.cn/zh-CN/audio.html |
| 翻译系统 | https://doc.renpy.cn/zh-CN/translation.html |
| 构建与分发 | https://doc.renpy.cn/zh-CN/build.html |

> 注：以上链接为 Ren'Py 官方中文文档。如需英文版，将 `zh-CN` 替换为 `en`。

## 3. 文件规范

### 3.1 命名约定

- `script.rpy` — 主剧本入口
- `script-章节.rpy` — 分章节剧本
- `characters.rpy` — 角色定义
- `screens.rpy` — 屏幕/界面
- `gui.rpy` — GUI 配置
- `options.rpy` — 游戏选项
- `definitions.rpy` — 全局定义（图像/音频/变换）
- `translation/` — 翻译文件目录

### 3.2 编码风格

- 缩进：4 空格
- 每行长度：不超过 120 字符
- 标签名：`snake_case`
- 变量名：`snake_case`
- 常量名：`UPPER_SNAKE_CASE`
- 角色名：`大写字母开头`（如 `main_character = Character("姓名")` 中的变量用 `mc`）

---

## 4. 修改流程

1. **先读文档**：找到项目文档中与被修改功能相关的部分
2. **理解上下文**：阅读要修改的 `.rpy` 文件的完整上下文（不仅仅是目标行）
3. **备份**：重要修改前确认有 Git 提交
4. **lint 验证**：修改后必须运行 `renpy <project> lint` 检查
5. **运行测试**：运行 `renpy <project> run` 确保游戏能正常启动

---

## 5. 常见陷阱

- **缩进错误**：Ren'Py 对缩进敏感，`if`/`while` 等块必须正确缩进
- **标签重复**：每个 `label` 在同一项目中必须唯一
- **图片路径**：引用图片时使用相对于 `game/` 的路径，如 `"images/bg/school.png"`
- **菜单语法**：`menu` 块内的每个选择项需缩进并对齐
- **变量作用域**：`default` 定义在 `label start` 之前，`$` 在运行时赋值
