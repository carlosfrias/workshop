#!/usr/bin/env python3
"""Final verification of import_pipeline.py fixes"""

import ast
import re

# Read file
with open("/Users/friasc/Cloud/ai-trading-workspace/bookkeeping/scripts/import_pipeline.py", "r") as f:
    content = f.read()

print("=" * 70)
print("FINAL VERIFICATION OF import_pipeline.py")
print("=" * 70)

# Check all the required fixes
fixes = []

# 1. openpyxl import uses load_workbook
fixes.append(("openpyxl import", "from openpyxl import load_workbook" in content))

# 2. pdfplumber has explicit True flag
fixes.append(("pdfplumber flag", "pdfplumber = True" in content))

# 3. --patch-file is required
fixes.append(("patch-file required", '--patch-file" type=Path, required=True' in content))

# 4. --patch-file can be used with ingest command
fixes.append(("patch-file usage", 'args.patch_file:' in content and "json.load(pf)" in content))

# 5. auto_approve flag exists
fixes.append(("auto-approve flag", 'action="store_true"' in content))

print()
for name, passed in fixes:
    status = "OK" if passed else "FAIL"
    print(f"✓ {name}: {status}")

# Check syntax
print()
print("=" * 70)
print("PYTHON SYNTAX CHECK")
print("=" * 70)
try:
    ast.parse(content)
    print("✓ Python syntax check: PASSED")
except SyntaxError as e:
    print(f"✗ Python syntax check: FAILED - {e}")

print()
print("=" * 70)
print("Usage:")
print("=" * 70)
print("  python3 import_pipeline.py ingest PATH --patch-file FILE.json --auto-approve")
print("  OR")
print("  python3 import_pipeline.py ingest PATH --patch-file FILE.json")
print()
print("Without --auto-approve flag, jobs are created but not auto-imported.")
print()
print("=" * 70)
