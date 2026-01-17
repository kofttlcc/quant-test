
import re
import sys
import os

def extract_code_blocks(markdown_file):
    """
    Parses a markdown file and extracts code blocks.
    Returns a list of dicts: {'language': str, 'content': str, 'start_line': int}
    """
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{markdown_file}' not found.")
        return []

    blocks = []
    in_block = False
    start_line = 0
    language = ""
    content_lines = []

    # Regex for start of code block: ```python or just ```
    block_start_pattern = re.compile(r'^```(\w*)')
    block_end_pattern = re.compile(r'^```\s*$')

    for i, line in enumerate(lines):
        line = line.rstrip()
        
        if not in_block:
            match = block_start_pattern.match(line)
            if match:
                in_block = True
                start_line = i + 1
                language = match.group(1) if match.group(1) else "text"
                content_lines = []
        else:
            if block_end_pattern.match(line):
                in_block = False
                blocks.append({
                    'language': language,
                    'start_line': start_line,
                    'content': '\n'.join(content_lines)
                })
            else:
                content_lines.append(line)

    return blocks

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_code_blocks.py <path_to_skill.md>")
        sys.exit(1)

    filepath = sys.argv[1]
    blocks = extract_code_blocks(filepath)

    print(f"Found {len(blocks)} code blocks in {filepath}:\n")
    for idx, block in enumerate(blocks):
        preview = block['content'][:50].replace('\n', ' ') + "..." if len(block['content']) > 50 else block['content']
        print(f"[{idx+1}] Language: {block['language']}, Line: {block['start_line']}")
        print(f"    Preview: {preview}")
        print("-" * 40)
