#!/usr/bin/env python3
"""Fix patch-file argument handling in import_pipeline.py"""

with open("/Users/friasc/Dropbox/ai-trading-workspace/bookkeeping/scripts/import_pipeline.py", "r") as f:
    content = f.read()

# Fix 1: Mark patch-file as required
old_arg = 'p_ingest.add_argument("--patch-file", type=Path, default=None, help="JSON file mapping trade_ids to per-record patches")'
new_arg = 'p_ingest.add_argument("--patch-file", type=Path, required=True, help="JSON file mapping trade_ids to per-record patches")'
content = content.replace(old_arg, new_arg)

# Fix 2: Load patches in run_pipeline and pass to stage_import
old_patches = '    patches: Optional[dict] = None'
new_patches = '    patches: Optional[dict] = None\n    if args.patch_file:\n        with open(args.patch_file, "r", encoding="utf-8") as pf:\n            patches = pf.read()\n        print(f"PATCH FILE loaded: {args.patch_file}")'
content = content.replace(old_patches, new_patches)

# Write back
with open("/Users/friasc/Dropbox/ai-trading-workspace/bookkeeping/scripts/import_pipeline.py", "w") as f:
    f.write(content)

print("Done fixing import_pipeline.py")
