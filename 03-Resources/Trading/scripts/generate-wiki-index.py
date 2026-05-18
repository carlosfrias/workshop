#!/usr/bin/env python3
"""
Auto-generate index.md files for wiki directories that are linked but empty.
Usage: python3 scripts/generate-wiki-index.py [directory ...]
"""
import os, sys
from pathlib import Path

def generate_index(dir_path: Path) -> str:
    """Generate index.md listing all .md files in directory."""
    dir_name = dir_path.name.replace('-', ' ').replace('_', ' ').title()
    parent_name = dir_path.parent.name.replace('-', ' ').replace('_', ' ').title()
    title = f"{parent_name} — {dir_name}"

    files = sorted([f for f in dir_path.glob("*.md") if f.name != "index.md"])
    subdirs = sorted([d for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')])

    lines = [f"# {title}\n", f""]

    if files:
        lines.append("## Documents\n")
        for f in files:
            name = f.stem.replace('-', ' ').replace('_', ' ')
            lines.append(f"- [{name}]({f.name})")
        lines.append("")

    if subdirs:
        lines.append("## Subdirectories\n")
        for d in subdirs:
            lines.append(f"- [{d.name}]({d.name}/)")
        lines.append("")

    return "\n".join(lines)


def main():
    dirs = sys.argv[1:] if len(sys.argv) > 1 else []
    if not dirs:
        print("Usage: python3 scripts/generate-wiki-index.py <dir> [dir ...]")
        sys.exit(1)

    for d in dirs:
        path = Path(d)
        if not path.is_dir():
            print(f"SKIP: {d} is not a directory")
            continue
        index_path = path / "index.md"
        if index_path.exists():
            print(f"SKIP: {index_path} already exists")
            continue
        content = generate_index(path)
        index_path.write_text(content, encoding="utf-8")
        print(f"CREATED: {index_path}")


if __name__ == "__main__":
    main()
