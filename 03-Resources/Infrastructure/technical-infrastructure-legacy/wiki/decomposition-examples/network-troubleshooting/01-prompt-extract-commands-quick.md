# Sub-Task 1: Extract Quick Diagnosis Commands

## Instruction

Read the file `./technical-infrastructure/prompts/network-troubleshooting.md` and extract ONLY the commands from the "Quick Diagnosis" section (the numbered list with 5 items).

For each command, extract:
- The command string (exact text after `→`)
- A short label (2-4 words)

## Input

- File path: `./technical-infrastructure/prompts/network-troubleshooting.md`
- Section: "Quick Diagnosis" (first code block)

## Expected Output Format

```json
{
  "section": "quick_diagnosis",
  "commands": [
    {
      "label": "Ping gateway",
      "command": "ping -c 3 <gateway>"
    },
    {
      "label": "Ping internet",
      "command": "ping -c 3 8.8.8.8"
    },
    ... (5 total)
  ],
  "count": 5
}
```

## Verification Criteria

- [ ] Exactly 5 commands extracted
- [ ] Command strings are exact (no modifications)
- [ ] Labels are short and descriptive
- [ ] JSON is valid and parseable

## Example Output

```json
{
  "section": "quick_diagnosis",
  "commands": [
    {
      "label": "Ping gateway",
      "command": "ping -c 3 <gateway>"
    },
    {
      "label": "Ping internet",
      "command": "ping -c 3 8.8.8.8"
    },
    {
      "label": "Check DNS",
      "command": "ping -c 3 google.com"
    },
    {
      "label": "Check packets",
      "command": "sudo tcpdump -i <iface> -c 10"
    },
    {
      "label": "Isolate issue",
      "command": "Check other devices on LAN"
    }
  ],
  "count": 5
}
```

## Notes

- Do NOT include commands from other sections
- Preserve exact syntax including flags and placeholders
