from collections import defaultdict
import os
from src.config import logging

class SafeDict(defaultdict):
    def __missing__(self, key):
        return '{' + key + '}'

def render_template(template_path: str, context: dict) -> tuple:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file {template_path} not found.")
        
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    if not lines or not lines[0].startswith("Subject:"):
        raise ValueError("Template must start with 'Subject: ' on the first line.")
        
    subject_raw = lines[0][8:].strip()
    
    # Body is everything after the subject and any blank lines immediately following it
    body_lines = lines[1:]
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    body_raw = "\n".join(body_lines)
    
    safe_context = SafeDict(str, **context)
    
    subject = subject_raw.format_map(safe_context)
    body = body_raw.format_map(safe_context)
    
    return subject, body
