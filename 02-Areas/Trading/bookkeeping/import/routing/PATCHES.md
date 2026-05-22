# PATCHES — Patch File Format & Actions

**Section ID:** `import-patches`
**Size:** ~1.2KB | **LOD:** Medium | **Load:** When creating or reviewing patch files

---

## Patch File Format

```json
{
  "#SCHWAB-20260303-001": { "skip": true },
  "#SCHWAB-20260129-023": {
    "postings": [
      "  Assets:Brokerage:Cash  500.00 USD",
      "  Income:Trading:Interest  -500.00 USD"
    ]
  },
  "#SCHWAB-20260318-062": {
    "replace_narration": "Dividend payment — corrected"
  }
}
```

Patch files are JSON objects keyed by Trade ID. Each key maps to a set of actions applied to that record during ingestion.

## Supported Patch Actions

| Action | Type | Effect |
|--------|------|--------|
| `"skip": true` | Boolean | Omit the record from import entirely |
| `"postings": ["..."]` | Array of strings | Replace all postings for this record |
| `"replace_narration": "text"` | String | Change only the narration text |

## Usage

```bash
python3 scripts/import_pipeline.py ingest statement.pdf \
  --patch-file staging/patches/fixes.json --auto-approve
```

## Validation Rules

- Keys must match the `#SCHWAB-YYYYMMDD-NNN` Trade ID format
- JSON must be valid — validate structure before running ingest
- `"postings"` strings must follow Beancount account format (2-space indent, amount, currency)
- Each Trade ID can have one or more actions applied simultaneously

## Example Patches

See `staging/patches/example_patches.json` for complete examples of all patch action types.