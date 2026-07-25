# ✨ Zarkdown （版本1.1）

> **键盘友好型纯文本标记语言** —— 所有符号均位于键盘主键区，无需按 Shift 组合键。

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/yangzizhoudiwuxuande/zarkdown)](https://github.com/yangzizhoudiwuxuande/zarkdown/stargazers)

Zarkdown 是一种全新的纯文本标记语言，专为**快速写作**和**极致键盘效率**而设计。它适合用来写笔记、技术文档、博客文章，甚至可以作为配置文件的格式。

---

## 🎯 设计哲学

- **键盘友好**：所有语法符号都在主键区，手指不需要大范围移动
- **直观易记**：`/` 表示标题（像路径层级），`?` 表示加粗（像强调语气）
- **纯文本**：任何文本编辑器都能打开，人类可读性强
- **可扩展**：支持表格、代码块、脚注等高级功能

---

## 📜 完整语法表

| 效果 | 语法 | 示例 | 渲染为 |
| :--- | :--- | :--- | :--- |
| **标题 1~4 级** | `/` `//` `///` `////` + 空格 | `/ 大标题` | `<h1>`~`<h4>` |
| **粗体** | `?文字?` | `?重要?` | `<strong>` |
| **斜体** | `\文字\` | `\斜体\` | `<i>` |
| **删除线** | `-文字-` | `-删掉-` | `<del>` |
| **超链接** | `*文字*(链接)` | `*点击*(https://x.com)` | `<a>` |
| **图片** | `$图片名$(链接)` | `$logo$(./pic.png)` | `<img>` |
| **行内代码** | `~文字~` | `~npm i~` | `<code>` |
| **多行代码块** | `~语言` 开头 + `~` 结尾 | `~python`...`~` | `<pre><code>` |
| **无序列表** | `!文字`（行首） | `!苹果` | `<ul><li>` |
| **有序列表** | `•文字`（行首，U+2022） | `•第一` | `<ol><li>` |
| **引用** | `\|文字`（行首） | `\| 引文` | `<blockquote>` |
| **表格** | `\| 表头 \|` + `------` | 见下方示例 | `<table>` |
| **注释** | `<文字>`（不含URL） | `<备注>` | `<!-- -->` |
| **脚注** | `[数字]<文字>` | `[1]<说明>` | `<sup title="">` |
| **分割线** | `-----`（独占一行） | | `<hr>` |
| **转义** | `^` 加在任意符号前 | `^/ 不是标题` | 原样输出 |

---

## 🚀 快速上手

### 安装

```bash
# 克隆仓库
git clone https://github.com/yangzizhoudiwuxuande/zarkdown.git
cd zarkdown

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装
pip install -e .
```
---

## 使用

```bash
# 转换 .zkdn 文件为 .html
zarkdown example.zkdn -o example.html

# 直接输出到终端（不生成文件）
zarkdown example.zkdn
```
---

## 示例
创建一个`hello.zkdn`文件：
```zkdn
/ Zarkdown 欢迎页

?恭喜?，您的格式已经跑通了！

这里有一个链接：*点击访问*(https://github.com/yangzizhoudiwuxuande)

~python
print("Hello Zarkdown!")
~

```
然后运行：
```bash
zarkdown hello.zkdn -w
```
浏览器会自动打开，显示渲染后的 HTML 页面。修改 `hello.zkdn` 并保存，页面会自动刷新。
## 📸 效果预览
![Zarkdown 渲染效果](screenshot.png)

## 贡献
欢迎任何形式的贡献！你可以：

* 🐛 报告 Bug（在 Issues 中描述）
* 💡 提出新功能建议
* 📝 完善文档
* 🔧 提交 Pull Request
## 📄 许可证
本项目采用 MIT License 开源协议，你可以自由使用、修改、分发。
## ❤️ 致谢
感谢你阅读这份文档！如果觉得 Zarkdown 有趣，欢迎给项目点一颗 ⭐ 星，让更多人看到它。
## 📝 更新日志
**v1.1.0 (2026-07-25)**
* ✨ 新增 `-w` 监听模式，保存即自动重新转换
* ✨ 自动在浏览器中打开生成 HTML，实现实时预览
* 🐛 修复中文编码问题，兼容带 BOM 的 UTF-8 文件
* 🐛 修复 macOS 下相对路径打开失败的问题
* 📝 完善 README 文档，增加完整语法表和示例

**v1.0.0 (2026-07-25)**
* 🎉 首次发布，支持完整的 Zarkdown 语法


---

Happy Writing with Zarkdown!

## 联系
yangzizhou2026@outlook.com
