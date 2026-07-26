#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Zarkdown 核心转换引擎
支持嵌套语法、转义、实时预览
"""

import re
import sys
import argparse
import os
import time
import webbrowser

# ============================================================
# 1. 转义处理（^符号）
# ============================================================

def escape_text(text):
    """将 ^符号 替换为不可打印占位符"""
    def repl(m):
        return f'\x00ESC_{ord(m.group(1))}\x00'
    return re.sub(r'\^([/\\?~\-*$•|!<\[\]])', repl, text)

def unescape_text(text):
    """恢复占位符为原字符"""
    return re.sub(r'\x00ESC_(\d+)\x00', lambda m: chr(int(m.group(1))), text)

# ============================================================
# 2. 递归解析器（处理嵌套行内标记）
# ============================================================

class _InlineParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.n = len(text)

    def parse(self):
        """解析入口，返回处理后的 HTML 字符串"""
        parts = []
        while self.pos < self.n:
            ch = self.text[self.pos]
            
            # 0. 转义符 ^：直接跳过，原样输出下一个字符
            if ch == '^':
                self.pos += 1
                if self.pos < self.n:
                    parts.append(self.text[self.pos])
                    self.pos += 1
                continue

            # 1. 粗体 ?...?
            if ch == '?':
                parts.append(self._parse_until('?', '<strong>', '</strong>'))
            # 2. 斜体 \...\
            elif ch == '\\':
                parts.append(self._parse_until('\\', '<i>', '</i>'))
            # 3. 删除线 -...-
            elif ch == '-':
                parts.append(self._parse_until('-', '<del>', '</del>'))
            # 4. 行内代码 ~...~
            elif ch == '~':
                parts.append(self._parse_until('~', '<code>', '</code>'))
            # 5. 超链接 *文字*(链接)
            elif ch == '*':
                parts.append(self._parse_link())
            # 6. 普通文本
            else:
                parts.append(ch)
                self.pos += 1
                
        return ''.join(parts)

    def _parse_until(self, end_char, open_tag, close_tag):
        """解析成对出现的包裹符号（如 ? 或 \）"""
        self.pos += 1  # 跳过起始符号
        inner_chars = []
        
        while self.pos < self.n and self.text[self.pos] != end_char:
            ch = self.text[self.pos]
            # 内部也要处理转义
            if ch == '^':
                self.pos += 1
                if self.pos < self.n:
                    inner_chars.append(self.text[self.pos])
                    self.pos += 1
                continue
            inner_chars.append(ch)
            self.pos += 1
        
        # 跳过结束符号
        if self.pos < self.n and self.text[self.pos] == end_char:
            self.pos += 1
        
        # 关键：递归解析内部内容，实现嵌套
        inner_text = ''.join(inner_chars)
        parsed_inner = _InlineParser(inner_text).parse()
        return f'{open_tag}{parsed_inner}{close_tag}'

    def _parse_link(self):
        """解析超链接 *文字*(链接)"""
        self.pos += 1  # 跳过开头的 *
        text_start = self.pos
        
        # 查找中间的 *，作为文本结束
        while self.pos < self.n and self.text[self.pos] != '*':
            if self.text[self.pos] == '^':
                self.pos += 1
                if self.pos < self.n:
                    self.pos += 1
                continue
            self.pos += 1
        
        if self.pos >= self.n or self.text[self.pos] != '*':
            # 没有闭合的 *，按普通文本处理
            return '*' + self.text[text_start:self.pos]
        
        link_text = self.text[text_start:self.pos]
        self.pos += 1  # 跳过中间的 *
        
        # 检查后面是否紧跟 (
        if self.pos < self.n and self.text[self.pos] == '(':
            self.pos += 1
            url_start = self.pos
            
            while self.pos < self.n and self.text[self.pos] != ')':
                self.pos += 1
            
            if self.pos < self.n and self.text[self.pos] == ')':
                url = self.text[url_start:self.pos]
                self.pos += 1  # 跳过 )
                
                # 递归解析文字部分（实现嵌套粗体、斜体等）
                parsed_text = _InlineParser(link_text).parse()
                return f'<a href="{url}">{parsed_text}</a>'
            else:
                return '*' + link_text + '*(' + self.text[url_start:self.pos]
        else:
            return '*' + link_text + '*'

# ============================================================
# 3. 行内解析入口（含注释、脚注、图片预处理）
# ============================================================

def parse_inline(text):
    """
    解析行内标记（支持嵌套）
    """
    # 1. 先处理转义（把 ^? 变成占位符，防止被解析器误匹配）
    escaped_text = escape_text(text)
    
    # 2. 处理注释（避开 URL 特征的 < >）
    def replace_comment(m):
        if re.search(r'https?://|ftp://|@', m.group(1)):
            return m.group(0)
        return f'<!-- {m.group(1)} -->'
    escaped_text = re.sub(r'<([^>]+)>', replace_comment, escaped_text)
    
    # 3. 处理脚注 [数字]<文字>
    escaped_text = re.sub(r'\[(\d+)\]<([^>]+)>', r'<sup title="\2">[\1]</sup>', escaped_text)
    
    # 4. 处理图片 $图片名$(链接)（图片不支持嵌套，直接正则）
    escaped_text = re.sub(r'\$(.+?)\$\(([^\)]+)\)', r'<img src="\2" alt="\1">', escaped_text)
    
    # 5. 调用递归解析器处理粗体、斜体、删除线、行内代码、超链接
    parser = _InlineParser(escaped_text)
    result = parser.parse()
    
    # 6. 恢复转义字符（把占位符还原为原始字符）
    result = unescape_text(result)
    return result

# ============================================================
# 4. 块级解析（标题、列表、表格、代码块等）
# ============================================================

def zarkdown_to_html(text):
    """将 Zarkdown 格式的文本转换为完整的 HTML 页面"""
    lines = text.split('\n')
    result, i = [], 0

    while i < len(lines):
        raw_line = lines[i]
        escaped_line = escape_text(raw_line)

        # ---- 多行代码块 ----
        if re.match(r'^~[a-zA-Z0-9_]+$', raw_line.strip()):
            lang = raw_line.strip()[1:]
            code_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '~':
                code_lines.append(lines[i])
                i += 1
            if i < len(lines) and lines[i].strip() == '~':
                i += 1
            result.append(f'<pre><code class="language-{lang}">{"\n".join(code_lines)}</code></pre>')
            continue

        # ---- 表格 ----
        if re.match(r'^\|.*\|$', escaped_line) and i + 2 < len(lines):
            next_esc = escape_text(lines[i+1])
            after_esc = escape_text(lines[i+2]) if i+2 < len(lines) else ''
            if re.match(r'^-{5,}$', next_esc.strip()) and re.match(r'^\|.*\|$', after_esc):
                headers = [h.strip() for h in escaped_line.split('|')[1:-1]]
                html = ['<table><thead><tr>']
                for h in headers:
                    html.append(f'<th>{parse_inline(h)}</th>')
                html.append('</tr></thead><tbody>')
                j = i + 2
                while j < len(lines):
                    cur_esc = escape_text(lines[j])
                    if re.match(r'^-{5,}$', cur_esc.strip()):
                        j += 1
                        continue
                    if re.match(r'^\|.*\|$', cur_esc):
                        cells = [c.strip() for c in cur_esc.split('|')[1:-1]]
                        html.append('<tr>')
                        for c in cells:
                            html.append(f'<td>{parse_inline(c)}</td>')
                        html.append('</tr>')
                        j += 1
                        continue
                    break
                html.append('</tbody></table>')
                result.append(''.join(html))
                i = j
                continue

        # ---- 标题 ----
        if re.match(r'^//// ', escaped_line):
            result.append(f'<h4>{parse_inline(escaped_line[5:])}</h4>')
        elif re.match(r'^/// ', escaped_line):
            result.append(f'<h3>{parse_inline(escaped_line[4:])}</h3>')
        elif re.match(r'^// ', escaped_line):
            result.append(f'<h2>{parse_inline(escaped_line[3:])}</h2>')
        elif re.match(r'^/ ', escaped_line):
            result.append(f'<h1>{parse_inline(escaped_line[2:])}</h1>')
        
        # ---- 无序列表 ----
        elif escaped_line.startswith('!'):
            items = []
            while i < len(lines) and escape_text(lines[i]).startswith('!'):
                items.append(f'<li>{parse_inline(escape_text(lines[i])[1:].strip())}</li>')
                i += 1
            result.append(f'<ul>{"".join(items)}</ul>')
            continue
        
        # ---- 有序列表 ----
        elif escaped_line.startswith('•'):
            items = []
            while i < len(lines) and escape_text(lines[i]).startswith('•'):
                items.append(f'<li>{parse_inline(escape_text(lines[i])[1:].strip())}</li>')
                i += 1
            result.append(f'<ol>{"".join(items)}</ol>')
            continue

        # ---- 引用 ----
        elif escaped_line.startswith('|'):
            result.append(f'<blockquote>{parse_inline(escaped_line[1:].strip())}</blockquote>')
        
        # ---- 分割线 ----
        elif re.match(r'^-{5,}$', escaped_line.strip()):
            result.append('<hr>')
        
        # ---- 普通段落 ----
        else:
            if raw_line.strip():
                result.append(f'<p>{parse_inline(escaped_line)}</p>')
            else:
                result.append('')
        i += 1

    # 生成完整的 HTML 页面
    html_content = '\n'.join(result)
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zarkdown 输出</title>
    <style>
        body {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #1e1e2f;
            background-color: #fafafa;
        }}
        h1, h2, h3, h4 {{ color: #1e1e2f; margin-top: 1.5em; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 0.3em; }}
        blockquote {{
            margin: 1.2em 0;
            padding: 0.8em 1.2em;
            border-left: 4px solid #4a90d9;
            background-color: #f0f4ff;
            border-radius: 0 4px 4px 0;
            color: #2c3e50;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            font-size: 0.95em;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        pre {{
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        code {{
            font-family: "SF Mono", "Fira Code", monospace;
            font-size: 0.9em;
        }}
        hr {{
            border: none;
            border-top: 2px dashed #ccc;
            margin: 2em 0;
        }}
        sup {{
            background: #eee;
            padding: 0.1em 0.4em;
            border-radius: 4px;
            font-size: 0.75em;
            cursor: help;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>'''

# ============================================================
# 5. 命令行入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="将 Zarkdown 文件转为 HTML")
    parser.add_argument("input", help="输入的 .zkdn 文件路径")
    parser.add_argument("-o", "--output", help="输出的 HTML 文件路径（默认：输入文件名替换为 .html）", default=None)
    parser.add_argument("-w", "--watch", action="store_true", help="监听文件变化，自动重新转换并刷新浏览器")
    args = parser.parse_args()

    # 自动生成输出文件名
    if args.output is None:
        args.output = args.input.replace('.zkdn', '.html')
        if args.output == args.input:  # 如果输入不是 .zkdn 结尾
            args.output += '.html'

    def convert():
        """执行转换并打开浏览器"""
        try:
            with open(args.input, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            html = zarkdown_to_html(content)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {args.input} -> {args.output}  ({time.strftime('%H:%M:%S')})")
            # 使用绝对路径 + file:// 协议打开
            webbrowser.open('file://' + os.path.abspath(args.output))
        except Exception as e:
            print(f"❌ 转换出错: {e}")

    # 首次转换
    convert()

    if args.watch:
        print(f"👀 正在监听 {args.input} 的变化（按 Ctrl+C 停止）...")
        try:
            last_mtime = os.path.getmtime(args.input)
            while True:
                current_mtime = os.path.getmtime(args.input)
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    convert()
                time.sleep(0.5)  # 每 0.5 秒检查一次
        except KeyboardInterrupt:
            print("\n👋 停止监听")

if __name__ == "__main__":
    main()
