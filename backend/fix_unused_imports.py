#!/usr/bin/env python3
"""
Fix F401 (unused imports) and F841 (unused variables)

This script uses autoflake to automatically remove unused imports and variables.
"""

import subprocess
import sys
from pathlib import Path


def run_autoflake():
    """Run autoflake to remove unused imports and variables"""
    backend_dir = Path(__file__).parent

    # autoflake command
    cmd = [
        sys.executable, '-m', 'autoflake',
        '--in-place',
        '--remove-all-unused-imports',
        '--remove-unused-variables',
        '--recursive',
        '--exclude', 'venv,__pycache__,.pytest_cache,migrations,instance,flask_session',
        str(backend_dir)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("autoflake not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'autoflake'])
        # Try again
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0


if __name__ == '__main__':
    print("Running autoflake to remove unused imports and variables...")
    if run_autoflake():
        print("\nSuccess! Unused imports and variables removed.")
    else:
        print("\nFailed to run autoflake.")
