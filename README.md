# ✨ Zarkdown （版本2.0.1）

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
### 转为HTML
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
### 转为Word/LaTex
转为Word/LaTex需要安装Pandoc。

```bash
brew install pandoc
```

转为Word
```bash
zarkdown my_note.zkdn -f docx
```

转为LaTex
```bash
zarkdown my_note.zkdn -f latex
```

## 📸 效果预览
[![pm4y4lF.png](https://s41.ax1x.com/2026/08/01/pm4y4lF.png)](https://imgchr.com/i/pm4y4lF)

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
**v2.0.1 (2026-08-01)**
- **语法错误检查器**  
  转换前自动扫描全文，检测未闭合的成对符号（`?`、`\`、`-`、`~`、`*`、`$`、`[`、`<`），并精确报告行号和列号，帮助用户快速定位问题。

- **括号配对检查**  
  针对超链接 `*文字*(链接)` 和图片 `$图片名$(链接)`，自动检测缺失的闭合括号 `)`，避免生成无效链接。

- **多行表格支持**  
  表格单元格内允许换行，通过缩进续行自动合并内容，并在输出中转换为 `<br>` 换行符。

- **转义字符 `^`**  
  在任意特殊符号前添加 `^` 即可原样输出，避免被解析器处理，例如 `^/ 不是标题`。

- **智能跳过机制**  
  错误检查器自动跳过分割线（以 `-----` 开头的行）、表格分隔行以及多行代码块内部内容，避免误报。

- **自动生成输出文件名**  
  若不指定 `-o`，输出文件名将根据输入文件名和格式自动生成（如 `note.html`、`note.pdf` 等）。

**v2.0.0 (2026-07-28)**
* 支持导出为Word/LaTex等格式（需安装Pandoc）

**v1.2.2 (2026-07-26)**
* 支持多行表格

**v1.2.1 (2026-07-26)**
* 支持嵌套语法（粗体里套斜体、超链接里套粗体等）


**v1.2.0 (2026-07-25)**
* 使引用和表格变得更好看

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
