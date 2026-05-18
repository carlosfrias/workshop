# Sub-Task 14: Check if r8168 Driver is Loaded

## Instruction

Check if the r8168 kernel module (correct driver) is currently loaded.

## Command to Execute

```bash
lsmod | grep r8168
```

## Expected Output Format

```json
{
  "task": "check_r8168",
  "r8168_loaded": true,
  "raw_output": "r8168 131072 0",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `r8168_loaded` is boolean (true if `lsmod | grep r8168` returns a line)
- [ ] `raw_output` contains the grep output (or empty string if not found)
- [ ] `exit_code` is 0 if found, 1 if not found
- [ ] JSON is valid and parseable

## Example: r8168 IS Loaded (Good)

```json
{
  "task": "check_r8168",
  "r8168_loaded": true,
  "raw_output": "r8168 131072 0",
  "exit_code": 0
}
```

## Example: r8168 NOT Loaded (Problem)

```json
{
  "task": "check_r8168",
  "r8168_loaded": false,
  "raw_output": "",
  "exit_code": 1
}
```

## Notes

- exit_code 0 from grep means "found" (r8168 IS loaded)
- exit_code 1 from grep means "not found" (r8168 NOT loaded)
- r8168 loaded = correct driver for Realtek RTL8168H chipsets
