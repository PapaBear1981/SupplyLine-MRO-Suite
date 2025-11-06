#!/usr/bin/env python3
"""
Final flake8 violation fixer

Fixes remaining issues:
- E302/E305/E306: Blank line issues
- F401: Unused imports
- F841: Unused variables
- E722: Bare except clauses
- E711: Comparison to None
"""

import ast
import re
from pathlib import Path


def fix_blank_lines_between_defs(content):
    """Fix E302/E305: Add 2 blank lines before top-level function/class definitions"""
    lines = content.split("\n")
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if this is a top-level function or class definition
        if (stripped.startswith(("def ", "class "))) and not line.startswith(" "):
            # Count preceding blank lines
            blank_count = 0
            j = i - 1
            while j >= 0 and not lines[j].strip():
                blank_count += 1
                j -= 1

            # Check if previous non-blank line is a decorator
            is_after_decorator = j >= 0 and lines[j].strip().startswith("@")

            # Need 2 blank lines before top-level def/class (unless after decorator or at start)
            if j >= 0 and not is_after_decorator and blank_count < 2:
                # Add missing blank lines
                for _ in range(2 - blank_count):
                    fixed_lines.append("")

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)


def remove_unused_imports(file_path, content):
    """Remove unused imports (F401)"""
    lines = content.split("\n")

    # Parse to find what's actually used
    try:
        ast.parse(content)
    except SyntaxError:
        return content  # Can't parse, skip

    # Common unused imports to remove
    unused_patterns = [
        (r"^from flask import session$", "session"),
        (r"^from flask import jsonify$", "jsonify"),
        (r"^from flask import make_response$", "make_response"),
        (r"^import sys$", "sys"),
        (r"^from datetime import timezone$", "timezone"),
        (r"^import time$", "time"),
        (r"^from collections import defaultdict$", "defaultdict"),
        (r"^import os$", "os"),
        (r"^from sqlalchemy import func$", "func"),
        (r"^from sqlalchemy import extract$", "extract"),
        (r"^from sqlalchemy\.orm import joinedload$", "joinedload"),
    ]

    fixed_lines = []
    for line in lines:
        should_remove = False
        for pattern, name in unused_patterns:
            if re.match(pattern, line.strip()):
                # Simple check: if name appears only in this import line, remove it
                if content.count(name) == line.count(name):
                    should_remove = True
                    break

        if not should_remove:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_bare_except(content):
    """Fix E722: Replace bare except with except Exception"""
    # Replace bare except: with except Exception:
    return re.sub(r"(\s+)except:\s*$", r"\1except Exception:", content, flags=re.MULTILINE)


def fix_none_comparison(content):
    """Fix E711: Use 'is None' instead of '== None'"""
    # Replace == None with is None
    content = re.sub(r"==\s*None\b", "is None", content)
    # Replace != None with is not None
    return re.sub(r"!=\s*None\b", "is not None", content)


def remove_unused_variables(content):
    """Fix F841: Remove or use unused variables"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Common pattern: except Exception as e: where e is unused
        if re.search(r"except\s+\w+\s+as\s+e:", line):
            # Replace 'as e' with just the exception type
            fixed_line = re.sub(r"(\s+except\s+\w+)\s+as\s+e:", r"\1:", line)
            line = fixed_line

        # Pattern: variable = something where variable is never used
        # This is harder to detect automatically, so we'll skip for now

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_file(file_path):
    """Apply all fixes to a file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes in order
        content = fix_bare_except(content)
        content = fix_none_comparison(content)
        content = remove_unused_variables(content)
        content = remove_unused_imports(file_path, content)
        content = fix_blank_lines_between_defs(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix final flake8 issues in all Python files"""
    backend_dir = Path(__file__).parent

    # Directories to process
    dirs_to_process = [
        backend_dir,
        backend_dir / "auth",
        backend_dir / "security",
        backend_dir / "utils",
        backend_dir / "tests",
    ]

    # Directories to exclude
    exclude_dirs = {"venv", "__pycache__", ".pytest_cache", "migrations", "instance", "flask_session"}

    files_fixed = 0
    files_processed = 0

    for directory in dirs_to_process:
        if not directory.exists():
            continue

        for file_path in directory.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            # Skip the fix scripts themselves
            if "fix_flake8" in file_path.name:
                continue

            files_processed += 1
            if fix_file(file_path):
                files_fixed += 1
                print(f"Fixed: {file_path.relative_to(backend_dir)}")

    print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")


if __name__ == "__main__":
    main()
