#!/usr/bin/env python3
"""
Fix F821 undefined name 'e' errors

This script fixes cases where 'as e' was removed from except clauses
but the variable 'e' is still referenced in the except block.
"""

import re
from pathlib import Path


def fix_undefined_e(content):
    """Fix undefined 'e' by restoring 'as e' in except clauses"""
    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is an except clause without 'as e'
        if re.search(r'except\s+\w+:', line) and 'as e' not in line:
            # Look ahead to see if 'e' is referenced in the except block
            indent = len(line) - len(line.lstrip())
            j = i + 1
            references_e = False

            while j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())

                # If we've dedented, we're out of the except block
                if next_line.strip() and next_indent <= indent:
                    break

                # Check if this line references 'e'
                if re.search(r'\be\b', next_line):
                    references_e = True
                    break

                j += 1

            # If 'e' is referenced, add 'as e' back
            if references_e:
                line = re.sub(r'(except\s+\w+):', r'\1 as e:', line)

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)


def fix_file(file_path):
    """Apply fixes to a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        content = fix_undefined_e(content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix undefined 'e' errors in all Python files"""
    backend_dir = Path(__file__).parent

    dirs_to_process = [
        backend_dir,
        backend_dir / 'auth',
        backend_dir / 'security',
        backend_dir / 'utils',
        backend_dir / 'tests',
    ]

    exclude_dirs = {'venv', '__pycache__', '.pytest_cache', 'migrations', 'instance', 'flask_session'}

    files_fixed = 0
    files_processed = 0

    for directory in dirs_to_process:
        if not directory.exists():
            continue

        for file_path in directory.rglob('*.py'):
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            if 'fix_flake8' in file_path.name or 'fix_undefined' in file_path.name:
                continue

            files_processed += 1
            if fix_file(file_path):
                files_fixed += 1
                print(f"Fixed: {file_path.relative_to(backend_dir)}")

    print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")


if __name__ == '__main__':
    main()
