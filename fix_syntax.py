#!/usr/bin/env python3
"""Fix escaped quote syntax errors in AI engine files."""

import re
from pathlib import Path

# Files to fix
files_to_fix = [
    "backend/app/ai/balloon_engine.py",
    "backend/app/ai/confidence_engine.py",
]

for file_path_str in files_to_fix:
    file_path = Path(file_path_str)
    if file_path.exists():
        content = file_path.read_text()
        # Replace escaped quotes with regular quotes
        content = content.replace('\\"', '"')
        file_path.write_text(content)
        print(f"Fixed: {file_path}")
    else:
        print(f"Not found: {file_path}")

print("Done fixing syntax errors!")
