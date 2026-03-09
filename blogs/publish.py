#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import re
from datetime import datetime

TEMPLATE_FILE = "blog-post-template.html"

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def publish_blog(source_file, target_file, title, category, date=None):
    if not date:
        date = datetime.now().strftime("%B %d, %2026") # Keeping the 2026 theme from the guide

    print(f"--- Starting publication of {source_file} ---")

    # 1. Convert to HTML fragment using pandoc
    fragment_file = "fragment.html"
    run_command(f"pandoc \"{source_file}\" -f {get_format(source_file)} -t html --mathjax -o {fragment_file}")

    # 2. Read fragment and clean it up
    with open(fragment_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cleanup artifacts (like LaTeX longtable artifacts)
    content = content.replace('<td colspan="3" style="text-align: right;"><em>Continued on next page</em></td>', '')
    content = content.replace('<tr>\n<td colspan="3" style="text-align: right;"><em>Continued on next page</em></td>\n</tr>', '')

    # 3. Read template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # 4. Handle relative paths for nested directories
    target_dir = os.path.dirname(target_file)
    depth = 0 if not target_dir else len(target_dir.split(os.sep))
    root_prefix = "../" * (depth + 1)
    
    # Robustly replace paths using regex
    # Replace style.css
    template = re.sub(r'href="\.\./style\.css"', f'href="{root_prefix}style.css"', template)
    # Replace index.html (with or without anchor)
    template = re.sub(r'href="\.\./index\.html(#\w+)?"', f'href="{root_prefix}index.html\\1"', template)
    # Replace profile image
    template = re.sub(r'src="\.\./images/profile\.png"', f'src="{root_prefix}images/profile.png"', template)

    # 5. Inject metadata and content
    # Update <title>
    template = re.sub(r'<title>.*?</title>', f'<title>{title} — Andy Zhang</title>', template)
    # Update date
    template = re.sub(r'<span class="blog-date">.*?</span>', f'<span class="blog-date">{date}</span>', template)
    # Update category
    template = re.sub(r'<span class="blog-category">.*?</span>', f'<span class="blog-category">{category}</span>', template)
    # Update H1 title
    template = re.sub(r'<h1 class="blog-post-title gradient-text">.*?</h1>', f'<h1 class="blog-post-title gradient-text">{title}</h1>', template)
    
    # Inject content into article
    content_safe = content.replace('\\', '\\\\')
    pattern = re.compile(r'(<article class="blog-content tex2jax_process">).*?(</article>)', re.DOTALL)
    new_html = pattern.sub(f'\\1\n{content_safe}\n\\2', template)

    # 6. Ensure parent directory exists
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 7. Write to target file
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_html)

    # 8. Cleanup
    if os.path.exists(fragment_file):
        os.remove(fragment_file)

    print(f"--- Successfully published to {target_file} ---")

def get_format(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.tex': return 'latex'
    if ext == '.md': return 'markdown'
    if ext == '.docx': return 'docx'
    return 'markdown'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate blog publishing from LaTeX, Markdown, or Word.")
    parser.add_argument("source", help="Source file (.tex, .md, .docx)")
    parser.add_argument("target", help="Target HTML filename (e.g., my-post.html or game/game.html)")
    parser.add_argument("--title", required=True, help="Blog title")
    parser.add_argument("--category", default="Mathematics", help="Blog category")
    parser.add_argument("--date", help="Publish date (default: today)")

    args = parser.parse_args()
    publish_blog(args.source, args.target, args.title, args.category, args.date)
