#!/usr/bin/env python3
"""
Automated flake8 violation fixer

This script automatically fixes common flake8 violations:
- W293: blank line contains whitespace
- W291: trailing whitespace
- W391: blank line at end of file
- W292: no newline at end of file
- E303: too many blank lines
"""

import re
from pathlib import Path


def fix_whitespace_issues(file_path):
    """Fix whitespace-related flake8 violations"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        lines = content.split("\n")

        # Fix W293: blank line contains whitespace
        # Fix W291: trailing whitespace
        fixed_lines = []
        for line in lines:
            # Remove trailing whitespace
            fixed_line = line.rstrip()
            fixed_lines.append(fixed_line)

        content = "\n".join(fixed_lines)

        # Fix W391: blank line at end of file
        # Fix W292: no newline at end of file
        # Ensure exactly one newline at end
        content = content.rstrip("\n") + "\n"

        # Fix E303: too many blank lines (max 2)
        # Replace 3+ consecutive blank lines with 2
        content = re.sub(r"\n\n\n+", "\n\n\n", content)

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
    """Fix whitespace issues in all Python files"""
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

            files_processed += 1
            if fix_whitespace_issues(file_path):
                files_fixed += 1
                print(f"Fixed: {file_path.relative_to(backend_dir)}")

    print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")


if __name__ == "__main__":
    main()
