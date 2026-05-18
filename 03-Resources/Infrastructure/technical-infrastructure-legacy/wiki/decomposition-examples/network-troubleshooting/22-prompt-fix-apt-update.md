# Sub-Task 22: Execute apt update

## Instruction

Execute `sudo apt update` to refresh the package list. This is the first step in the driver fix procedure.

## Command to Execute

```bash
sudo apt update
```

## Expected Output Format

```json
{
  "task": "fix_apt_update",
  "step": 1,
  "success": true,
  "raw_output": "Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease\nGet:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease...\nFetched 12.3 MB in 3s (4,123 kB/s)\nReading package lists... Done",
  "exit_code": 0
}
```

## Verification Criteria

- [ ] `success` is boolean (true if exit_code is 0)
- [ ] `raw_output` contains the actual apt output
- [ ] `exit_code` is 0 (success) or non-zero (failure)
- [ ] `step` is 1 (first step in fix procedure)
- [ ] JSON is valid and parseable

## Example: Success

```json
{
  "task": "fix_apt_update",
  "step": 1,
  "success": true,
  "raw_output": "Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease\nGet:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease...\nFetched 12.3 MB in 3s (4,123 kB/s)\nReading package lists... Done",
  "exit_code": 0
}
```

## Example: Failure (No Internet)

```json
{
  "task": "fix_apt_update",
  "step": 1,
  "success": false,
  "raw_output": "Err:1 http://archive.ubuntu.com/ubuntu jammy InRelease\n  Temporary failure resolving 'archive.ubuntu.com'\nReading package lists... Done\nE: Failed to fetch some archives",
  "exit_code": 100
}
```

## Notes

- This step requires internet connectivity
- If this fails, the node needs temporary internet (USB tethering) before proceeding
- Do NOT continue to Step 2 if this fails
