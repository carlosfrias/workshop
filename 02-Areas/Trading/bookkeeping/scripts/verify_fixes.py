#!/usr/bin/env python3
import ast
import re

# Read file
with open("import_pipeline.py", "r") as f:
    content = f.read()

# Check syntax
try:
    ast.parse(content)
    print("Python AST check: OK")
except SyntaxError as e:
    print(f"Syntax error: {e}")

# Check key fixes
checks = [
    ("openpyxl import", "from openpyxl import load_workbook" in content),
    ("pdfplumber flag", "pdfplumber = True" in content),
]

for name, passed in checks:
    result = "OK" if passed else "FAIL"
    print(f"{name}: {result}")

# Verify patch-file argument
if '--patch-file' in content and 'required=True' in content:
    # Ensure it's linked to patch_file in run_pipeline
    print("patch-file argument: CHECK (needs additional context verification)")
else:
    print("patch-file argument: FAIL")
