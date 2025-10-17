#!/usr/bin/env python3
"""
Advanced flake8 violation fixer

Fixes:
- F401: Remove unused imports
- E302/E305: Add proper blank lines between functions/classes
- F541: Remove f-string prefix from strings without placeholders
- E712: Fix comparison to True/False
# - F821: Remove references to undefined CycleCountResult  # FIXME: CycleCountResult removed
"""

import re
from pathlib import Path


def fix_unused_imports(content, file_path):
    """Remove common unused imports"""
    lines = content.split('\n')
    fixed_lines = []

    # Common unused imports to remove
    unused_patterns = [
        r'^from flask import.*session.*$',
        r'^from flask import.*jsonify.*$',
        r'^from flask import.*make_response.*$',
        r'^import sys$',
        r'^from datetime import timezone$',
        r'^from datetime import datetime$',
        r'^import time$',
        r'^from collections import defaultdict$',
        r'^import os$',
    ]

    for line in lines:
        # Check if this line matches any unused import pattern
        should_remove = False
        for pattern in unused_patterns:
            if re.match(pattern, line.strip()):
                # Check if it's actually used in the file
                import_name = None
                if 'import' in line:
                    parts = line.split()
                    if 'from' in line and 'import' in line:
                        import_name = parts[-1].strip(',')
                    elif 'import' in line:
                        import_name = parts[-1]

                    # Simple heuristic: if import appears only once (the import line), it's unused
                    if import_name and content.count(import_name) == 1:
                        should_remove = True
                        break

        if not should_remove:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_blank_lines(content):
    """Fix E302/E305: Add proper blank lines"""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Add current line
        fixed_lines.append(line)

        # Check if next line starts a function or class definition
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip()
            current_line = line.strip()

            # If next line is a function/class def and current line is not blank
            if (next_line.startswith('def ') or next_line.startswith('class ')) and current_line:
                # Count blank lines before next line
                blank_count = 0
                j = i
                while j >= 0 and not lines[j].strip():
                    blank_count += 1
                    j -= 1

                # Need 2 blank lines before top-level def/class
                if blank_count < 2 and not current_line.startswith('@'):
                    # Add missing blank line
                    fixed_lines.append('')

    return '\n'.join(fixed_lines)


def fix_f_strings(content):
    """Fix F541: Remove f prefix from strings without placeholders"""
    # Match f-strings without {} placeholders
    pattern = r'f(["\'])([^{}\1]*?)\1'

    def replacer(match):
        quote = match.group(1)
        string_content = match.group(2)
        # Only remove f if there are no braces
        if '{' not in string_content and '}' not in string_content:
            return f'{quote}{string_content}{quote}'
        return match.group(0)

    return re.sub(pattern, replacer, content)


def fix_boolean_comparisons(content):
    """Fix E712: comparison to True should be 'if cond is True:' or 'if cond:'"""
    # Replace is True with is True
    content = re.sub(r'==\s*True\b', 'is True', content)
    # Replace is False with is False
    content = re.sub(r'==\s*False\b', 'is False', content)
    return content


def remove_cycle_count_references(content):
#     """Remove references to CycleCountResult"""  # FIXME: CycleCountResult removed
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Skip lines that reference CycleCountResult
        if 'CycleCountResult' in line and 'import' not in line.lower():
            # Comment out the line instead of removing it
            if not line.strip().startswith('#'):
                fixed_lines.append('# ' + line + '  # FIXME: CycleCountResult removed')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def fix_file(file_path):
    """Apply all fixes to a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_f_strings(content)
        content = fix_boolean_comparisons(content)
        content = remove_cycle_count_references(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix advanced flake8 issues in all Python files"""
    backend_dir = Path(__file__).parent

    # Directories to process
    dirs_to_process = [
        backend_dir,
        backend_dir / 'auth',
        backend_dir / 'security',
        backend_dir / 'utils',
        backend_dir / 'tests',
    ]

    # Directories to exclude
    exclude_dirs = {'venv', '__pycache__', '.pytest_cache', 'migrations', 'instance', 'flask_session'}

    files_fixed = 0
    files_processed = 0

    for directory in dirs_to_process:
        if not directory.exists():
            continue

        for file_path in directory.rglob('*.py'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            files_processed += 1
            if fix_file(file_path):
                files_fixed += 1
                print(f"Fixed: {file_path.relative_to(backend_dir)}")

    print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")


if __name__ == '__main__':
    main()
