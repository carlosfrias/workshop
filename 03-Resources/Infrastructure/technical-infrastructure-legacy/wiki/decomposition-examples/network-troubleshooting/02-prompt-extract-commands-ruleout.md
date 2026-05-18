# Sub-Task 2: Extract "What to Rule Out" Commands

## Instruction

Read the file `./technical-infrastructure/prompts/network-troubleshooting.md` and extract ONLY the commands from the "What to Rule Out (Before Assuming Driver)" table.

For each row in the table, extract:
- The check name
- The command (from the "Command" column)
- What to do if negative (from the third column)

## Input

- File path: `./technical-infrastructure/prompts/network-troubleshooting.md`
- Section: "What to Rule Out" table

## Expected Output Format

```json
{
  "section": "what_to_rule_out",
  "checks": [
    {
      "check": "Router Access Control",
      "command": "Check router admin UI",
      "if_negative": "Disable all, retest"
    },
    ... (9 total)
  ],
  "count": 9
}
```

## Verification Criteria

- [ ] Exactly 9 checks extracted
- [ ] Commands are exact (including `sudo` if present)
- [ ] JSON is valid and parseable

## Notes

- Some rows have commands like "Check router admin UI" — include these as-is
- Include all rows from the table
