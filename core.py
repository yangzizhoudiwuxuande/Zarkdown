import re
import sys
import argparse

def escape_text(text):
    """将 ^符号 替换为不可打印占位符"""
    def repl(m):
        return f'\x00ESC_{ord(m.group(1))}\x00'
    # 注意：- 放在字符类最末尾或最开头，[ 需要转义
    return re.sub(r'\^([/\\?~\-*$•|!<\[\]])', repl, text)

def unescape_text(text):
    """恢复占位符为原字符"""
    return re.sub(r'\x00ESC_(\d+)\x00', lambda m: chr(int(m.group(1))), text)

def parse_inline(text):
    """解析行内标记"""
    text = escape_text(text)
    
    # 1. 注释（避开 URL）
    def replace_comment(m):
        if re.search(r'https?://|ftp://|@', m.group(1)):
            return m.group(0)
        return f'<!-- {m.group(1)} -->'
    text = re.sub(r'<([^>]+)>', replace_comment, text)

    # 2. 脚注 -> 上标悬浮
    text = re.sub(r'\[(\d+)\]<([^>]+)>', r'<sup title="\2">[\1]</sup>', text)
    # 3. 超链接（优先于普通星号）
    text = re.sub(r'\*([^\*]+)\*\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    # 4. 图片
    text = re.sub(r'\$(.+?)\$\(([^\)]+)\)', r'<img src="\2" alt="\1">', text)
    # 5. 行内代码
    text = re.sub(r'~(.+?)~', r'<code>\1</code>', text)
    # 6. 粗体
    text = re.sub(r'\?(.+?)\?', r'<strong>\1</strong>', text)
    # 7. 斜体
    text = re.sub(r'\\(.+?)\\', r'<i>\1</i>', text)
    # 8. 删除线
    text = re.sub(r'-(.+?)-', r'<del>\1</del>', text)
    
    return unescape_text(text)

def zarkdown_to_html(text):
    """将 Zarkdown 格式的文本转换为 HTML"""
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

    # 用完整的 HTML 框架包裹内容
    html_content = '\n'.join(result)
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zarkdown 输出</title>
</head>
<body>
{html_content}
</body>
</html>'''

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="将 Zarkdown 文件转为 HTML")
    parser.add_argument("input", help="输入的 .zkdn 文件路径")
    parser.add_argument("-o", "--output", help="输出的 HTML 文件路径", default=None)
    args = parser.parse_args()
    
    try:
        # ⭐ 使用 utf-8-sig 编码，自动处理 BOM 头，解决中文乱码
        with open(args.input, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取文件时出错：{e}")
        sys.exit(1)
    
    html = zarkdown_to_html(content)
    
    if args.output:
        # ⭐ 使用 'w' 模式写入，并指定 utf-8 编码
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ 已转换到 {args.output}")
    else:
        print(html)

if __name__ == "__main__":
    main()
